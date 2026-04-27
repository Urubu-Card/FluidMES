from plasmic import clp_conn as conn
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import asyncio


class Modbus_Control:

    def __init__(self,ip:str,port:int):
        self.conexao = conn.Conexao(ip,port)
        self.conectar = self.conexao.Conectar()
        self.cliente = self.conexao.cliente


    def Ler_Coil(self,adress:int):

        try:

            leitor = self.cliente.read_coils(adress)

            if not leitor.isError():
                dado = bool(leitor.bits[0])
                return dado
            else:
                return f"Erro ao tentar ler :{leitor}" 
       
        except ModbusException as e:
            return f"Ocorreu um erro : {e}"

        


    def Escrever_Coil(self,adress:int,value:bool):
        """Essa DEF escreve em uma porta COIl apenas valores booleanos """
       
        try:
            add = self.cliente.write_coil(address=adress,value=value)

            if bool(add) == True:
                return f" O valor {value} foi registrado com sucesso na coil {adress}"

            else:
                return f"Ocorreu um erro ao tentar registar a Coil : {add}"

        except ModbusException as e:
            return f"Ocorreu um erro : {e}"
        
        finally:
            self.conexao.FecharConexao()


    async def Ler_Coil_RealTime(self, adress: int):
        try:
            i = 0
            while True:
                leitor = self.cliente.read_coils(adress)
                if not leitor.isError():
                    dado = str(bool(leitor.bits[0])).upper()
                    print(f"Requisição {i} | Coil {adress} está no estado: {dado}")
                    i += 1
                    await asyncio.sleep(0.5)
                else:
                    print(f"Erro ao tentar ler: {leitor}")
                    break

        except ModbusException as e:
            print(f"Ocorreu um erro: {e}")
        except KeyboardInterrupt:
            print("Ação encerrada")
        finally:
            self.conexao.FecharConexao()


    def InputStatus(self,adress:int):
        """Input Status só pode ler valores BOOL e não pode escrever.(como IS so tem uma funcionalidade é mais facil explicar o que o IS faz)"""

        try:
            leitor = self.cliente.read_discrete_inputs(adress)

            if not leitor.isError():
                dado = leitor.bits[0]
                print(f"O registro está no estado {str(bool(dado)).upper()}")
            else:
                print(f"Erro ao tentar ler :{leitor}")   
       
        except ModbusException as e:
            print(f"Ocorreu um erro : {e}")

        finally:
            self.conexao.FecharConexao()


    def HoldingRegister(self,adress:int):

        try:
            leitor = self.cliente.read_holding_registers(adress)

            if not leitor.isError():
                print(f"O valor do registro é: {leitor.registers[0]}")
            else:
                print(f"Erro ao tentar ler: {leitor}")   

        except ModbusException as e:
            print(f"Ocorreu um erro: {e}")

        finally:
            self.conexao.FecharConexao()


    async def HoldingRegisterRealTime(self,adress:int):

        try:
            i = 0 
            while True:
                leitor = self.cliente.read_holding_registers(adress)

                if not leitor.isError():
                    print(f"Requisição {i} valor: {leitor.registers[0]}")
                    i +=1
                
                    await asyncio.sleep(0.5)
                else:
                    print(f"Erro : {leitor}")
                    break

        except ModbusException as e:
            print(f"Ocorreu um erro: {e}")

        except KeyboardInterrupt :
            print("Ação encerrada")

        finally:
            self.conexao.FecharConexao()


    def Escrever_Registro(self,adress:int,value:float):

        try:
            print("a")

        except ModbusException as E:
            print(f"Occoreu um erro: {E}")
        

        finally:
            self.conexao.FecharConexao()


if __name__ == "__main__":
    IP = "127.0.0.1"

    PORT = 5020


    app = Modbus_Control(ip= IP,port=PORT)
    print(app.Escrever_Coil(4,False))
    


