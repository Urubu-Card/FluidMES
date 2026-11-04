import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.middleware.csrf import get_token
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .models import PasswordResetToken
from .serializers import (CadastroSerializer, LoginSerializer, UsuarioSerializer,
                          PasswordRestRequestSerializer, PasswordRestConfirmSerializer, FuncionarioSerializer)
from .permissions import OwnerAccess, EmployeeDirectoryAccess
from .audit import AuditMixin, record

User = get_user_model()
logger = logging.getLogger(__name__)

class AuthThrottle(AnonRateThrottle):
    scope = 'auth'

class PublicView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthThrottle]
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        SessionAuthentication().enforce_csrf(request)

class CsrfView(PublicView):
    throttle_classes = []
    def get(self, request):
        return Response({'csrfToken': get_token(request)})

def set_jwt_cookies(response, access_token, refresh_token):
    for key, token, lifetime in (
        (settings.AUTH_COOKIE_ACCESS, access_token, 'ACCESS_TOKEN_LIFETIME'),
        (settings.AUTH_COOKIE_REFRESH, refresh_token, 'REFRESH_TOKEN_LIFETIME'),
    ):
        response.set_cookie(key, str(token), max_age=settings.SIMPLE_JWT[lifetime],
                            secure=settings.AUTH_COOKIE_SECURE, httponly=True,
                            samesite=settings.AUTH_COOKIE_SAMESITE)
    return response

def clear_cookies(response):
    for key in (settings.AUTH_COOKIE_ACCESS, settings.AUTH_COOKIE_REFRESH):
        response.delete_cookie(key, samesite=settings.AUTH_COOKIE_SAMESITE)
    return response

class CadastroView(PublicView):
    def post(self, request):
        serializer = CadastroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            raise ValidationError('CPF, CNPJ ou e-mail já cadastrado.')
        return Response(UsuarioSerializer(user).data, status=status.HTTP_201_CREATED)

class LoginView(PublicView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        update_last_login(None, user)
        return set_jwt_cookies(Response(UsuarioSerializer(user).data), refresh.access_token, refresh)

class LogoutView(PublicView):
    def post(self, request):
        token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        if token:
            try:
                RefreshToken(token).blacklist()
            except TokenError:
                pass
        return clear_cookies(Response({'detail': 'Logout efetuado.'}))

class TokenRefreshCookieView(PublicView):
    def post(self, request):
        try:
            refresh = RefreshToken(request.COOKIES.get(settings.AUTH_COOKIE_REFRESH, ''))
            user = User.objects.get(pk=refresh['user_id'], is_active=True)
        except (TokenError, User.DoesNotExist, KeyError):
            return clear_cookies(Response({'detail': 'Sessão inválida ou expirada.'}, status=401))
        # Password changes invalidate existing refresh and access credentials.
        from rest_framework_simplejwt.utils import get_md5_hash_password
        if refresh.get('hash_password') != get_md5_hash_password(user.password):
            return clear_cookies(Response({'detail': 'Sessão inválida.'}, status=401))
        return set_jwt_cookies(Response({'detail': 'Sessão renovada.'}), refresh.access_token, refresh)

class MeView(APIView):
    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)

class PasswordResetRequestView(PublicView):
    def post(self, request):
        serializer = PasswordRestRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(email__iexact=serializer.validated_data['email'], is_active=True).first()
        if user:
            reset = PasswordResetToken.objects.create(user=user)
            link = f'{settings.FRONTEND_URL}/auth/reset-password?token={reset.token}'
            try:
                send_mail('Redefinição de senha — FluidMES',
                          f'Use este link em até uma hora: {link}',
                          settings.DEFAULT_FROM_EMAIL, [user.email])
            except Exception:
                reset.delete()
                logger.exception('Falha no envio de recuperação de senha')
        return Response({'detail': 'Se o e-mail existir, enviaremos as instruções.'})

class PasswordRestConfirmView(PublicView):
    @transaction.atomic
    def post(self, request):
        serializer = PasswordRestConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset = PasswordResetToken.objects.select_for_update().filter(token=serializer.validated_data['token']).first()
        if not reset or not reset.is_valid():
            raise ValidationError('Token expirado ou inválido.')
        user = User.objects.select_for_update().get(pk=reset.user_id)
        # Conditional consumption also prevents replay on SQLite.
        if not PasswordResetToken.objects.filter(pk=reset.pk, used=False).update(used=True):
            raise ValidationError('Token já utilizado.')
        user.set_password(serializer.validated_data['nova_senha'])
        user.save(update_fields=['password'])
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)
        return clear_cookies(Response({'detail': 'Senha redefinida.'}))

class FuncionariosView(AuditMixin, ModelViewSet):
    audit_resource = "funcionário"
    serializer_class = FuncionarioSerializer
    permission_classes = [EmployeeDirectoryAccess]
    def get_queryset(self):
        return User.objects.filter(empresa=self.request.user.empresa).exclude(role=1).select_related('empresa').order_by('id')
    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save(empresa=self.request.user.empresa)
                record(self.request.user, self.request.user.empresa_id, 'criou', 'funcionário', serializer.instance.get_full_name())
        except IntegrityError:
            raise ValidationError('CPF ou e-mail já cadastrado.')
    def perform_update(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
                record(self.request.user, self.request.user.empresa_id, 'editou', 'funcionário', serializer.instance.get_full_name())
        except IntegrityError:
            raise ValidationError('CPF ou e-mail já cadastrado.')


class PreferenciasView(APIView):
    def get(self, request):
        from .models import Preferencias
        from .serializers import PreferenciasSerializer
        prefs, _ = Preferencias.objects.get_or_create(usuario=request.user)
        return Response(PreferenciasSerializer(prefs).data)
    def patch(self, request):
        from .models import Preferencias
        from .serializers import PreferenciasSerializer
        prefs, _ = Preferencias.objects.get_or_create(usuario=request.user)
        serializer = PreferenciasSerializer(prefs, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class AtualizacoesView(APIView):
    permission_classes = [OwnerAccess]
    def get(self, request):
        from .models import Atualizacao
        from .serializers import AtualizacaoSerializer
        from rest_framework.pagination import LimitOffsetPagination
        query = Atualizacao.objects.filter(empresa=request.user.empresa).exclude(autor=request.user)
        pagination = LimitOffsetPagination()
        pagination.default_limit = 30
        pagination.max_limit = 100
        page = pagination.paginate_queryset(query, request)
        return pagination.get_paginated_response(AtualizacaoSerializer(page, many=True).data)


class ConfigurarEmpresaView(APIView):
    """Let authenticated orphan accounts create their own company, never join another tenant."""
    @transaction.atomic
    def post(self, request):
        from .models import Empresa
        from .serializers import ConfigurarEmpresaSerializer
        user = User.objects.select_for_update().get(pk=request.user.pk)
        if user.empresa_id:
            raise ValidationError('Sua conta já está vinculada a uma empresa.')
        serializer = ConfigurarEmpresaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                company = Empresa.objects.create(**serializer.validated_data)
        except IntegrityError:
            raise ValidationError('CNPJ já cadastrado.')
        user.empresa = company
        user.role = user.Role.PREPOSTO
        user.save(update_fields=['empresa','role'])
        return Response(UsuarioSerializer(user).data, status=201)
