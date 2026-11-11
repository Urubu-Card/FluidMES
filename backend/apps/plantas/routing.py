from django.urls import path
from .consumers import PlantMonitorConsumers

websocket_urlpatterns = [path("ws/plant/<uuid:uuid>/", PlantMonitorConsumers.as_asgi())]
