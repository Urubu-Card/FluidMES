"""Leitura avulsa e confirmação de comandos Modbus."""

from pymodbus.exceptions import ModbusException
from services.clp_control import Modbus_Control

from services.modbus_map import ENDERECOS_TANQUES

ERROS_MODBUS = (OSError, ModbusException, IndexError, ValueError)


async def ler_modo(clp, tanque):
    """Leitura ao vivo do registro MODO, feita antes de qualquer comando."""
    cliente = Modbus_Control(clp.ip, clp.porta, retries=0)
    try:
        await cliente.Conectar()
        return (await cliente.HoldingRegister(ENDERECOS_TANQUES[tanque]["MODO"]))[0]
    finally:
        cliente.conexao.FecharConexao()


async def consultar(sensor, *, comando=None):
    clp = sensor.clp
    cliente = Modbus_Control(clp.ip, clp.porta, retries=0)
    leitores = {
        "coil": cliente.Ler_Coil,
        "input_status": cliente.InputStatus,
        "holding_register": cliente.HoldingRegister,
    }
    try:
        await cliente.Conectar()
        if comando is not None:
            if sensor.tipo_registro == "coil":
                await cliente.Escrever_Coil(sensor.endereco, comando)
            else:
                await cliente.Write_Register(sensor.endereco, comando)
        try:
            valores = await leitores[sensor.tipo_registro](sensor.endereco)
            return float(valores[0])
        except ERROS_MODBUS:
            if comando is None:
                raise
            # O CLP já confirmou a escrita. A leitura de retorno é independente.
            return None
    finally:
        cliente.conexao.FecharConexao()
