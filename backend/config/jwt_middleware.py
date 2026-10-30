from http.cookies import SimpleCookie, CookieError
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError

@database_sync_to_async
def authenticate(token):
    try:
        auth = JWTAuthentication()
        return auth.get_user(auth.get_validated_token(token))
    except (AuthenticationFailed, TokenError):
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        cookies = SimpleCookie()
        try:
            cookies.load(dict(scope.get('headers', [])).get(b'cookie', b'').decode())
        except (CookieError, UnicodeError):
            pass
        token = cookies.get(settings.AUTH_COOKIE_ACCESS)
        scope['auth_token'] = token.value if token else None
        scope['user'] = await authenticate(token.value) if token else AnonymousUser()
        return await self.app(scope, receive, send)
