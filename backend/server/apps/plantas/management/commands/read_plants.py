import asyncio
from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from services.clp_control import Modbus_Control
from apps.plantas.models import Clp, Sensor
from asgiref.sync import sync_to_async
from redis.exceptions import ConnectionError
import re
import time


def busca_clps():
    dados = []
    resultado =  Clp.objects.filter(ativo=True)
    for clp in resultado:
        dados.append ( {
            "id": clp.idclp,
            "nome":clp.nome,
            "ip":clp.ip,
            "porta":clp.porta,
            "uuid":clp.planta.uuid
        })
    return dados
        
def busca_sensores_um_clp(clpID):
    dados= {}
    sensores = Sensor.objects.filter(clp=clpID)
    sensores_do_clp = []
    for sensor in sensores:
            sensores_do_clp.append({
                "tipo": sensor.tipo_registro,
                "endereco": sensor.endereco,
            })
    return sensores_do_clp
        
        
def busca_sensores(clps):
    dados = {}
    for clp in clps:
        resultado = Sensor.objects.filter(clp=clp['id'])
        sensores_do_clp = []
        for sensor in resultado:
            sensores_do_clp.append({
                "tipo": sensor.tipo_registro,
                "endereco": sensor.endereco,
            })
        dados[clp['id']] = sensores_do_clp
    return dados



class Command(BaseCommand):
    
    help = "Comando Modbus para distrubuição dos WebSockets"
    
    INTERVALO = 30 #*30 segundos de intervalo para a busca no banco
    
    async def verificar_conexao(self,client):
        while True:
                try:
                    await client.Conectar()
                    if client.isConnected():
                        break
                    else:
                        self.stdout.write(self.style.ERROR(f"Não foi possivel conectar ao servidor: IP{client.conexao.ip} PORT{client.conexao.porta}"))
                        await asyncio.sleep(5)
                except Exception as e:
                    self.stdout.write(self.style.NOTICE(f"{e}"))
                    await asyncio.sleep(5)
    
    
    async def poll_loop(self,id, uuid, ip, port, sensores):
        channel_layer = get_channel_layer()
        client = Modbus_Control(ip,port)
        await client.Conectar()

        if not client.isConnected():
            await self.verificar_conexao(client)

        if bool(sensores) is False:
            self.stdout.write(self.style.ERROR("Nenhum sensor registrado ao clp"))
            return
            
        try:
            counter = 0
            while True:
                if not client.isConnected():
                    await self.verificar_conexao(client)
                if counter % self.INTERVALO ==0:
                    sensores = await sync_to_async(busca_sensores_um_clp)(id)
                
                data = {}
                
                for sensor in sensores:
                    tipo     = sensor['tipo']
                    endereco = sensor['endereco']
                    if tipo == 'coil':
                        resultado = await client.Ler_Coil(endereco, 1)
                    elif tipo == 'input_status':
                        resultado = await client.InputStatus(endereco, 1)
                    elif tipo == 'holding_register':
                        resultado = await client.HoldingRegister(endereco, 1)
                    else:
                        self.stdout.write(self.style.WARNING(f"Tipo desconhecido: {tipo}"))#? Era impossivel de acontecer XD
                        continue
                    data[f"{tipo}_{endereco}"] = resultado[0] if resultado is not None else None

                if data:
                    try:
                        await channel_layer.group_send(
                            f'plant_{uuid}',
                            {'type': "plant.update", 'data': data}
                        )
                        self.stdout.write(f"Enviando para {uuid} data:{data}")
                    except ConnectionError as e:
                        self.stdout.write(self.style.WARNING(f"Redis não conectado : {e}"))
                else:
                    self.stdout.write(self.style.WARNING("Data não foi realizada"))

                counter += 1
                await asyncio.sleep(1)

        finally:
            client.conexao.FecharConexao()

                
    def handle(self, *args, **options): 
        asyncio.run(self.main())
        
        
    async def main(self,):

        clps = await sync_to_async(busca_clps)()#? Genial isso ele primeiro transforma e depois chama
        sensores = await sync_to_async(busca_sensores)(clps)
        lista_de_clps =[]
        for clp in clps:
            sensores_do_clp =sensores[clp['id']]
            lista_de_clps.append(self.poll_loop(clp['id'],clp['uuid'],clp['ip'],clp['porta'],sensores_do_clp))
            
        await asyncio.gather(*lista_de_clps)
