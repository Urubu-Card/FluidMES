import clp_conn as conn
from pymodbus.exceptions import ModbusException
import asyncio


class Modbus_Control:

    def __init__(self, ip: str, port: int):
        self.conexao  = conn.Conexao(ip, port)
        self.conectar = self.conexao.Conectar()
        self.cliente  = self.conexao.cliente

    def isConnected(self):
        return bool(self.conectar)

    def Ler_Coil(self, adress: int):
        try:
            leitor = self.cliente.read_coils(adress)
            if not leitor.isError():
                return bool(leitor.bits[0])
            return f'Erro ao ler: {leitor}'
        except ModbusException as e:
            return f'Erro: {e}'

    def Escrever_Coil(self, adress: int, value: bool):
        try:
            resultado = self.cliente.write_coil(address=adress, value=value)
            if bool(resultado):
                return f'Valor {value} registrado na coil {adress}'
            return f'Erro ao escrever na coil: {resultado}'
        except ModbusException as e:
            return f'Erro: {e}'
        finally:
            self.conexao.FecharConexao()

    async def Ler_Coil_RealTime(self, adress: int):
        try:
            i = 0
            while True:
                leitor = self.cliente.read_coils(adress)
                if not leitor.isError():
                    dado = str(bool(leitor.bits[0])).upper()
                    print(f'Req {i} | Coil {adress}: {dado}')
                    i += 1
                    await asyncio.sleep(0.5)
                else:
                    break
        except (ModbusException, KeyboardInterrupt):
            pass
        finally:
            self.conexao.FecharConexao()

    def InputStatus(self, adress: int):
        try:
            leitor = self.cliente.read_discrete_inputs(adress)
            if not leitor.isError():
                return bool(leitor.bits[0])
            return f'Erro: {leitor}'
        except ModbusException as e:
            return f'Erro: {e}'
        finally:
            self.conexao.FecharConexao()

    def HoldingRegister(self, adress: int):
        try:
            leitor = self.cliente.read_holding_registers(adress)
            if not leitor.isError():
                return leitor.registers[0]
            return f'Erro: {leitor}'
        except ModbusException as e:
            return f'Erro: {e}'
        finally:
            self.conexao.FecharConexao()

if __name__ == "__main__":
    client = Modbus_Control("127.0.0.1",5020)
    client.Escrever_Coil(0,False)