from rest_framework.views                     import APIView
from rest_framework.response                  import Response
from rest_framework                           import status , permissions
from rest_framework_simplejwt.tokens          import RefreshToken
from apps.accounts.models                     import PasswordResetToken
from apps.accounts.serializers                import CadastroSerializer, LoginSerializer , UsuarioSerializer , PasswordRestRequestSerializer,PasswordRestConfirmSerializer
from django.contrib.auth                      import get_user_model
from django.core.mail                         import send_mail
from django.conf                              import settings

User = get_user_model()

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
            send_mail(
                subject="Redefinição de senha - FluidMES",
                message=f"Clique no link para redefinir sua senha: {link}\nExpira em 1 hora.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],

            )
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
        serializer = LoginSerializer(data=request.data,context={'request': request})
        
        
        if serializer.is_valid():
            user    = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'acess'  : str(refresh.access_token),
                'refresh': str(refresh),
                'usuario': UsuarioSerializer(user).data,
            })
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    
    
    def post(self,request):
        
        try:
            refresh = request.data['refresh']
            token   = RefreshToken(refresh)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)   
        
class MeView(APIView):
    
    def get(self,request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(UsuarioSerializer(request.user).data)

        