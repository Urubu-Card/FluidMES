import os
from rest_framework.views                     import APIView
from rest_framework.response                  import Response
from rest_framework                           import status , permissions
from rest_framework_simplejwt.tokens          import RefreshToken
from apps.accounts.models                     import PasswordResetToken
from apps.accounts.serializers                import CadastroSerializer, LoginSerializer , UsuarioSerializer , PasswordRestRequestSerializer,PasswordRestConfirmSerializer
from django.contrib.auth.models               import update_last_login
from django.contrib.auth                      import get_user_model
from django.core.mail                         import EmailMultiAlternatives
from django.conf                              import settings
from django.template.loader                   import render_to_string
from background_task                          import background
from email.mime.image                         import MIMEImage

User = get_user_model()

def set_jwt_cookies(response, access_token, refresh_token):
    response.set_cookie(
        key=settings.AUTH_COOKIE_ACCESS,
        value=str(access_token),
        expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
    response.set_cookie(
        key=settings.AUTH_COOKIE_REFRESH,
        value=str(refresh_token),
        expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
        secure=settings.AUTH_COOKIE_SECURE,
        httponly=settings.AUTH_COOKIE_HTTPONLY,
        samesite=settings.AUTH_COOKIE_SAMESITE,
    )
    return response

class Emails:
    @background(schedule=1)
    def welcome(username,empresa,email):
        contexto = {
            'username': username,
            'nome_empresa': empresa,
            'email_usuario': email,
            'login_url': f"{settings.FRONTEND_URL}/login",
        }
        html_content = render_to_string('registration/welcome.html', contexto)
        text_content = render_to_string('registration/welcome.html', contexto)

        email = EmailMultiAlternatives(
            subject="Bem-vindo à FluidMES!",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        email.attach_alternative(html_content, "text/html")

        logo_path = os.path.join(settings.BASE_DIR, 'assets/images/logo.png')
        with open(logo_path, 'rb') as f:
            logo = MIMEImage(f.read())
            logo.add_header('Content-ID', '<logo_fluidmes>')
            logo.add_header('Content-Disposition', 'inline', filename='logo_fluidmes.png')
            email.attach(logo)

        email.send()

    @background(schedule=0)
    def forgotEmail(primeiro_nome,link,user_email):

        context = {
                        'username':primeiro_nome,
                        'reset_url':link
                    }
        
        
        html_content = render_to_string('registration/password_forgot_email.html', context)
        text_content = render_to_string('registration/password_forgot_email.txt', context)
        msg = EmailMultiAlternatives(
            subject="Redefinição de senha - FluidMES",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],

        )

        msg.attach_alternative(html_content, "text/html")
        msg.send()

class CadastroView(APIView):
    
    def post(self, request ):
        
        serializer = CadastroSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            username = request.data.get("first_name")
            empresa  = request.data.get("nomeEmpresa")
            email    = request.data.get("email")
            Emails.welcome(username,empresa,email)
            return Response(
                status= status.HTTP_201_CREATED
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordRestRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        user = User.objects.filter(email__iexact=email).first()
        if user:
            reset_token =PasswordResetToken.objects.create(user=user)
            username=user.first_name
            link = f"{settings.FRONTEND_URL}/api/password-reset/confirm/?token={reset_token.token}"
            user_email = user.email

            Emails.forgotEmail(username[0],link,user_email)
            
            
        return Response(
            {"detail":"Se o email existir,enviamos as instruções para o redefinimento da senha"},
            status=status.HTTP_200_OK
        )   
    
class PasswordRestConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request,):
        serializer = PasswordRestConfirmSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        token_value = serializer.validated_data['token']
        nova_senha = serializer.validated_data['nova_senha']
        
        reset_token = PasswordResetToken.objects.filter(token=token_value).first()
        
        if not reset_token or not reset_token.is_valid():
            return Response({"detail":"Token espirado ou invalido"},status=status.HTTP_400_BAD_REQUEST)
        
        user = reset_token.user
        user.set_password(nova_senha)
        user.save()
        
        reset_token.used =True
        reset_token.save()
        
        PasswordResetToken.objects.filter(user=user, used=False).exclude(id=reset_token.id).update(used=True)
        
        return Response({"detail": "Senha Redefina com sucesso"},status=status.HTTP_200_OK)

class LoginView(APIView):
    
    def post(self,request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            update_last_login(None,user)
            response = Response(status=status.HTTP_200_OK)
            
    
            return set_jwt_cookies(response, refresh.access_token, refresh)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    
    
    def post(self,request):
        response = Response({"detail": "Logout efetuado com sucesso!"}, status=status.HTTP_200_OK)
        
        try:
            refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
            if refresh_token:
                token   = RefreshToken(refresh_token)
                token.blacklist()
            
        except Exception:
            pass

        response.delete_cookie(settings.AUTH_COOKIE_ACCESS, samesite=settings.AUTH_COOKIE_SAMESITE)
        response.delete_cookie(settings.AUTH_COOKIE_REFRESH, samesite=settings.AUTH_COOKIE_SAMESITE)

        return response

class TokenRefreshCookieView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)
        
        if not refresh_token:
            return Response({"detail": "Refresh token não encontrado nos cookies."}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
           
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token
            
            response = Response({"detail": "Token atualizado com sucesso!"}, status=status.HTTP_200_OK)
            
            response.set_cookie(
                key=settings.AUTH_COOKIE_ACCESS,
                value=str(new_access_token),
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTPONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE,
            )
            return response
            
        except Exception:
            return Response({"detail": "Refresh token inválido ou expirado."}, status=status.HTTP_401_UNAUTHORIZED)

class MeView(APIView):
    
    def get(self,request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(UsuarioSerializer(request.user).data)

        