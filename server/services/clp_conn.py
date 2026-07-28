# Movido de plasmic/clp_conn.py → services/clp_conn.py
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import logging

logging.getLogger('pymodbus').setLevel(logging.CRITICAL)


class Conexao:

    def __init__(self, ip: str, port: int):
        self.ip     = ip
        self.porta  = port
        self.cliente = None

    def Conectar(self):
        try:
            self.cliente = ModbusTcpClient(self.ip, port=self.porta)
            if not self.cliente.connect():
                self.cliente = None
            return self.cliente
        except ModbusException:
            self.cliente = None
            return None

    def FecharConexao(self):
        if self.cliente is not None:
            self.cliente.close()

if __name__ =="__main__":
    
    cliente = Conexao("127.0.0.1",5020)
    
    cliente