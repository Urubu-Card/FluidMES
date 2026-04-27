from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

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
            print (f"Ocorreu um erro na conexão : {e}")
            self.cliente=None
            return self.cliente
       

    def FecharConexao(self):

        self.cliente.close()
        


if __name__ == "__main__":
    conn = Conexao(ip="127.0.0.1",port="5020")
    conn.Conectar()
    print(conn.cliente)