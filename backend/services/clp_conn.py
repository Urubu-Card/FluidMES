
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
import logging
import asyncio
logger = logging.getLogger(__name__)
logging.getLogger('pymodbus').setLevel(logging.CRITICAL)


class Conexao:

    def __init__(self, ip: str, port: int):
        self.ip     = ip
        self.porta  = port
        self.cliente = None

    async def Conectar(self):
        "Faz a conexão com o CLP"
        self.FecharConexao()
        try:
            self.cliente = AsyncModbusTcpClient(host=self.ip, 
                                                port=self.porta,
                                                timeout=5.0,
                                                retries=3)
            await self.cliente.connect()
            if self.cliente.connected:
                return self.cliente

        except (ModbusException,Exception) as e:
            logger.warning("%s no IP:%s e na PORTA:%s.",e,self.ip,self.porta)
            self.cliente = None
            return self.cliente

    def FecharConexao(self):
        if self.cliente is not None:
            self.cliente.close()
            self.cliente = None



if __name__ =="__main__":
    async def main():
        conexao_clp = Conexao("999.1.1.1", 5020)
        
        cliente = await conexao_clp.Conectar()
        print(cliente)
    
    asyncio.run(main())