from django.urls import re_path
from  apps.plantas import consumers

websocket_urlpatterns = [
    re_path(r"ws/plant/(?P<uuid>[\w-]+)/$",consumers.PlantMonitorConsumers.as_asgi()),
]