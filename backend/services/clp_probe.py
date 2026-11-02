"""Read-only diagnostic; a TCP connection is distinct from a valid Modbus read."""

from .clp_control import Modbus_Control


async def probe(ip, port, sensor=None):
    client = Modbus_Control(ip, port)
    connected = False
    try:
        await client.Conectar()
        connected = True
        if not sensor:
            return dict(
                conectado=True,
                leitura_validada=False,
                mensagem="Conexão TCP estabelecida. Cadastre um sensor para validar uma leitura Modbus.",
            )
        method = {
            "coil": client.Ler_Coil,
            "holding_register": client.HoldingRegister,
            "input_status": client.InputStatus,
        }[sensor["tipo_registro"]]
        values = await method(sensor["endereco"])
        return dict(
            conectado=True,
            leitura_validada=True,
            valor=values[0],
            sensor=sensor["nome"],
            mensagem="CLP respondeu e a leitura Modbus foi validada.",
        )
    except Exception:
        return dict(
            conectado=connected,
            leitura_validada=False,
            mensagem=(
                "Conexão TCP estabelecida, mas a leitura falhou. Confira o tipo e o endereço do registro."
                if connected
                else "Não foi possível conectar ao CLP. Confira IP, porta e rede."
            ),
        )
    finally:
        client.conexao.FecharConexao()
