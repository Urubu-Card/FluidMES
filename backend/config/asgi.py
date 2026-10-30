import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

django_asgi_app = get_asgi_application()
from django.conf import settings
if settings.DEBUG:
    from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
    django_asgi_app = ASGIStaticFilesHandler(django_asgi_app)

from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from .jwt_middleware import JWTAuthMiddleware
from  apps.plantas import routing

application = ProtocolTypeRouter({
    'http':django_asgi_app,
    'websocket':AllowedHostsOriginValidator(JWTAuthMiddleware(
        URLRouter(routing.websocket_urlpatterns)
    ))
})