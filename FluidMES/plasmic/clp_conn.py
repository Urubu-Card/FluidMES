from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import logging

#! Remove o erro que fica dando quando não conecta
logging.getLogger("pymodbus").setLevel(logging.CRITICAL)


class Conexao:

    def __init__(self,ip:str,port:int):
        self.ip = ip
        self.porta = port
        self.cliente = None

    def Conectar(self):

        try:
            self.cliente = ModbusTcpClient(self.ip,port=self.porta)
        

            if not self.cliente.connect():
                self.cliente=None
                return self.cliente
           
            else:
                return self.cliente

        except ModbusException as e:
            self.cliente=None
            return self.cliente
       

    def FecharConexao(self):

        if self.cliente is not None:
            self.cliente.close()
        


if __name__ == "__main__":
    conn = Conexao(ip="127.0.0.1",port="5020")
    conn.Conectar()
    print(conn.cliente)