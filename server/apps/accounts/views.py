from rest_framework.views                     import APIView
from rest_framework.response                  import Response
from rest_framework                           import status , permissions
from rest_framework_simplejwt.tokens          import RefreshToken
from apps.accounts.models                     import PasswordResetToken
from apps.accounts.serializers                import CadastroSerializer, LoginSerializer , UsuarioSerializer , PasswordRestRequestSerializer,PasswordRestConfirmSerializer
from django.contrib.auth                      import get_user_model
from django.core.mail                         import EmailMultiAlternatives
from django.conf                              import settings
from django.template.loader                   import render_to_string

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


class CadastroView(APIView):
    
    def post(self, request ):
        
        serializer = CadastroSerializer(data=request.data)
        
        if serializer.is_valid():
            usuario = serializer.save()
            return Response(
                UsuarioSerializer(usuario).data,
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
            link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
            context = {
                'username':user.first_name,
                'reset_url':link
            }
            html_content = render_to_string('registration/password_reset_email.html', context)
            text_content = render_to_string('registration/password_reset_email.txt', context)
            msg = EmailMultiAlternatives(
                subject="Redefinição de senha - FluidMES",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],

            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
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
            
            response = Response({
                'usuario': UsuarioSerializer(user).data,
            }, status=status.HTTP_200_OK)
            
    
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
                return Response(status=status.HTTP_204_NO_CONTENT)
            
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

        