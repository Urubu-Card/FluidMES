import asyncio
from django.core.management.base import BaseCommand
from channels.layers import get_channel_layer
from services.clp_control import Modbus_Control
from apps.plantas.models import Clp, Sensor
from asgiref.sync import sync_to_async
import re


def busca_clps():
    dados = []
    resultado =  Clp.objects.filter(ativo=True)
    for clp in resultado:
        dados.append ( {
            "id": clp.idclp,
            "nome":clp.nome,
            "ip":clp.ip,
            "porta":clp.porta,
        })
    return dados
        
        
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
    
    async def poll_loop(self, nome, ip, port, sensores):
        channel_layer = get_channel_layer()
        client = Modbus_Control(ip, port)
        await client.Conectar()

        if not client.isConnected():
            self.stdout.write(self.style.ERROR("Não foi possivel conectar ao servidor"))
            return

        try:
            while True:
                data = {}

                for sensor in sensores:
                    tipo = sensor['tipo']
                    endereco = sensor['endereco']

                    if tipo == 'coil':
                        resultado = await client.Ler_Coil(endereco, 1)
                    elif tipo == 'input':
                        resultado = await client.InputStatus(endereco, 1)
                    elif tipo == 'holding':
                        resultado = await client.HoldingRegister(endereco, 1)
                    else:
                        self.stdout.write(self.style.WARNING(f"Tipo desconhecido: {tipo}"))#! IMPOSSIVEL DE ACONTECER REMOVER
                        continue

                    data[f"{tipo}_{endereco}"] = resultado[0]

                if data:
                    nome_planta = re.sub(r'[^a-zA-Z0-9._-]', '', nome)[:99]
                    await channel_layer.group_send(
                        f'plant_{nome_planta}',
                        {'type': "plant.update", 'data': data}
                    )
                    self.stdout.write(f"Enviando para {nome_planta} data:{data}")
                else:
                    self.stdout.write(self.style.WARNING("Deu merda"))

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
            lista_de_clps.append(self.poll_loop(clp['nome'],clp['ip'],clp['porta'],sensores_do_clp))
            
            
        await asyncio.gather(*lista_de_clps)