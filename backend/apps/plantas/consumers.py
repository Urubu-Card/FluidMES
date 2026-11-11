from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Planta


class PlantMonitorConsumers(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        uuid = self.scope["url_route"]["kwargs"]["uuid"]
        if not user.is_authenticated or not user.empresa_id:
            await self.close(code=4401)
            return
        allowed = await database_sync_to_async(
            Planta.objects.filter(uuid=uuid, empresa_id=user.empresa_id).exists
        )()
        if not allowed:
            await self.close(code=4403)
            return
        self.group_name = f"plant_{uuid}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def plant_update(self, event):
        from config.jwt_middleware import authenticate

        user = await authenticate(self.scope.get("auth_token") or "")
        if (
            not user.is_authenticated
            or user.empresa_id != self.scope["user"].empresa_id
        ):
            await self.close(code=4401)
            return
        await self.send_json(event["data"])
