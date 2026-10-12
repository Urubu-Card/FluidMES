from urllib.parse                           import parse_qs
from django.contrib.auth                    import get_user_model
from django.contrib.auth.models             import AnonymousUser
from rest_framework_simplejwt.tokens        import UntypedToken
from rest_framework_simplejwt.exceptions    import InvalidToken, TokenError
from asgiref.sync                           import sync_to_async
from http.cookies                           import SimpleCookie

def busca_usuario(user_id):
    User = get_user_model()
    try:
        usuario = User.objects.get(id=user_id)
        return usuario
    
    except User.DoesNotExist:
        return AnonymousUser()

def token_cookie(scope):
    headers = dict(scope['headers'])
    cookiesBytes = headers.get(b'cookie')
    if cookiesBytes is None:
        return None

    cookies = SimpleCookie(cookiesBytes.decode())

    acessToken = cookies.get('access_token')
    if acessToken:
        return acessToken.value
    else:
        return None

class JWTAuthMiddleware:
    
    def __init__(self,app):
        self.app = app
        
    async def __call__(self, scope,receive,send):
        query = scope['query_string'].decode('utf-8')
        dict_query = parse_qs(query)
        token = dict_query.get('token',[None])[0] or token_cookie(scope)
        scope["user"]= AnonymousUser()
        try:
            validated_token = UntypedToken(token)
            user_Id = validated_token['user_id'] 
            usuario = await sync_to_async(busca_usuario)(user_Id)
            scope["user"] = usuario
            
        except (InvalidToken,TokenError,KeyError):
            scope["user"]= AnonymousUser()
        
        return await self.app(scope, receive, send)
            