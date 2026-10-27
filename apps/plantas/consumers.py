import asyncio
import json
from   channels.generic.websocket import AsyncWebsocketConsumer
from apps.plantas.models import Planta
from asgiref.sync import sync_to_async

def busca_Planta(uuid,empresa):
    
    try:
        planta = Planta.objects.get(uuid=uuid,empresa_id=empresa)
        return planta
    except Planta.DoesNotExist:
        return None
        

class PlantMonitorConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = None
        uuid = self.scope['url_route']['kwargs']['uuid']
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        
        planta = await sync_to_async(busca_Planta)(uuid,self.scope['user'].empresa_id1)
        if planta is None:
            await self.close()
            return
        self.group_name =f"plant_{uuid}"
        await self.channel_layer.group_add(self.group_name,self.channel_name)
        await self.accept()
        
        
    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name,self.channel_name)
        
        
        
    async def plant_update(self, event):
        await self.send(text_data=json.dumps(event['data']))