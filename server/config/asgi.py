import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from .jwt_middleware import JWTAuthMiddleware
from  apps.plantas import routing

application = ProtocolTypeRouter({
    'http':django_asgi_app,
    'websocket':JWTAuthMiddleware(
        URLRouter(routing.websocket_urlpatterns)
    )
})