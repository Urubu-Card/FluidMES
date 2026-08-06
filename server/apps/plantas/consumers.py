import asyncio
import json
from   channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from apps.plantas.models import Planta
from asgiref.sync import sync_to_async

def busca_Planta(uuid,empresa):
    
    try:
        planta = Planta.objects.get(uuid=uuid,empresa=empresa)
        return planta
    except Planta.DoesNotExist:
        return None
        

class PlantMonitorConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        uuid = self.scope['url_route']['kwargs']['uuid']
        if isinstance(self.scope["user"]) == AnonymousUser() :
            await self.close()
            return
        
        planta  =await sync_to_async(busca_Planta)(uuid,self.scope['user'].empresa)
        if planta is None:
            await self.close()
            return
        self.group_name =f"plant_{uuid}"
        await self.channel_layer.group_add(self.group_name,self.channel_name)
        await self.accept()
        
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name,self.channel_name)
        
        
        
    async def plant_update(self, event):
        await self.send(text_data=json.dumps(event['data']))