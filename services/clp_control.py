from pymodbus.pdu import ExceptionResponse
from .clp_conn import Conexao

class EscritaRecusada(IOError):
    pass


class Modbus_Control:
    """Adapter returning values or exceptions, never error strings as measurements."""
    def __init__(self, ip: str, port: int, *, retries=1):
        self.conexao = Conexao(ip, port, retries=retries)
        self.cliente = None
    async def Conectar(self):
        self.cliente = await self.conexao.Conectar()
        return self.cliente
    def isConnected(self):
        return bool(self.cliente and self.cliente.connected)
    async def _read(self, method, address, count, field):
        if not self.isConnected():
            raise ConnectionError('CLP desconectado.')
        result = await getattr(self.cliente, method)(address=address, count=count)
        if result.isError():
            raise IOError(f'Falha Modbus: {result}')
        return list(getattr(result, field)[:count])
    async def Ler_Coil(self, address, count=1):
        return await self._read('read_coils', address, count, 'bits')
    async def InputStatus(self, address, count=1):
        return await self._read('read_discrete_inputs', address, count, 'bits')
    async def HoldingRegister(self, address, count=1):
        return await self._read('read_holding_registers', address, count, 'registers')
    async def _write(self, method, address, value):
        if not self.isConnected():
            raise ConnectionError('CLP desconectado.')
        argumento = 'values' if method == 'write_registers' else 'value'
        result = await getattr(self.cliente, method)(address=address, **{argumento: value})
        if isinstance(result, ExceptionResponse):
            raise EscritaRecusada(f"Código Modbus {result.exception_code}")
        if result.isError():
            raise IOError(f'Falha Modbus: {result}')
        return True
    async def Escrever_Coil(self, address, value):
        return await self._write('write_coil', address, value)
    async def Write_Register(self, address, value):
        return await self._write('write_register', address, value)
    async def Write_Registers(self, address, values):
        return await self._write('write_registers', address, list(values))
