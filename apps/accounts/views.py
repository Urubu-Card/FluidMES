from rest_framework.views            import APIView
from rest_framework.response         import Response
from rest_framework                  import status
from rest_framework_simplejwt.tokens import RefreshToken
from .sertializers                   import CadastroSerializer, LoginSerializer , UsuarioSerializer

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


class LoginView(APIView):
    
    def post(self,request):
        serializer = LoginSerializer(data=request.data,context={'request': request})
        
        
        if serializer.is_valid():
            user    = serializer.validated_data['user']
            print(user)
            print(user.id)
            print(type(user.id))
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

        