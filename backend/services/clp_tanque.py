"""Leitura e comando de um tanque (TK1/TK2) conforme mapeamento.xlsx.

O MES só comanda com MODO = 2. Em 0 (operação local) e 1 (aparelho) ele
apenas lê; quem tenta comandar recebe MesBloqueado.
"""

from .clp_control import Modbus_Control
from .modbus_map import (
    BOBINAS_PARTIDA,
    ENDERECOS_TANQUES,
    MODO_MES,
    REGISTROS_TANQUE,
    STATUS_EM_CICLO,
    modo_label,
)


class MesBloqueado(Exception):
    """O tanque não está no modo MES."""

    def __init__(self, modo):
        self.modo = modo
        super().__init__(
            f"Tanque em modo {modo} ({modo_label(modo)}). "
            "O MES só comanda com o MODO 2."
        )


class TanqueOcupado(Exception):
    """Já existe um ciclo em andamento no tanque."""


class ParametrosNaoConfirmados(IOError):
    """O CLP aceitou a escrita, mas a releitura não bate com a receita."""


async def ler(cliente: Modbus_Control, tanque):
    """Um único FC3 com os 10 registros do tanque, mais a bobina de partida."""
    enderecos = ENDERECOS_TANQUES[tanque]
    valores = await cliente.HoldingRegister(
        enderecos[REGISTROS_TANQUE[0]], len(REGISTROS_TANQUE)
    )
    if len(valores) != len(REGISTROS_TANQUE):
        raise IOError("Resposta Modbus incompleta.")
    r = dict(zip(REGISTROS_TANQUE, valores))
    try:
        partida = bool((await cliente.Ler_Coil(BOBINAS_PARTIDA[tanque]))[0])
    except (OSError, IndexError):
        partida = None  # A bobina é só informativa; os registros decidem.
    return dict(
        tanque=tanque,
        etapa=r["ETAPA"],
        niveis=[r["NIVEL1"], r["NIVEL2"], r["NIVEL3"]],
        nivel_atual=r["NIVEL_ATUAL"],
        tempos=[r["TEMPO1"], r["TEMPO2"], r["TEMPO3"]],
        status=r["STATUS"],
        modo=r["MODO"],
        start_cycle=partida,
    )


async def iniciar_ciclo(cliente: Modbus_Control, tanque, niveis, tempos):
    """Grava a receita, confere e aciona START_CYCLE. Exige MODO 2 e tanque livre."""
    estado = await ler(cliente, tanque)
    if estado["modo"] != MODO_MES:
        raise MesBloqueado(estado["modo"])
    if estado["status"] == STATUS_EM_CICLO:
        raise TanqueOcupado("O tanque já está em ciclo.")
    enderecos = ENDERECOS_TANQUES[tanque]
    niveis, tempos = [int(v) for v in niveis], [int(v) for v in tempos]
    await cliente.Write_Registers(enderecos["NIVEL1"], niveis)
    await cliente.Write_Registers(enderecos["TEMPO1"], tempos)
    estado = await ler(cliente, tanque)
    if estado["niveis"] != niveis or estado["tempos"] != tempos:
        raise ParametrosNaoConfirmados("O CLP não confirmou os parâmetros da receita.")
    if estado["modo"] != MODO_MES:
        raise MesBloqueado(estado["modo"])
    if estado["start_cycle"]:
        # Bobina presa em 1 de um ciclo anterior: rearma para gerar a borda.
        await cliente.Escrever_Coil(BOBINAS_PARTIDA[tanque], False)
    await cliente.Escrever_Coil(BOBINAS_PARTIDA[tanque], True)


async def rearmar_partida(cliente: Modbus_Control, tanque):
    """Devolve START_CYCLE a 0 depois do ciclo, para a próxima borda de subida."""
    await cliente.Escrever_Coil(BOBINAS_PARTIDA[tanque], False)
