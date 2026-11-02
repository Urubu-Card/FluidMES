"""Comportamento de bancada para os tanques da planilha Modbus."""

from dataclasses import dataclass
from time import monotonic

from pymodbus.constants import ExcCodes
from pymodbus.simulator import DataType, SimData, SimDevice

from .modbus_map import (
    BOBINAS_PARTIDA,
    CAMPOS_EDITAVEIS,
    ENDERECOS_TANQUES,
    MODO_LOCAL,
    MODO_MES,
    MODOS,
    STATUS_CONCLUIDO,
    STATUS_EM_CICLO,
    STATUS_PARADO,
)


@dataclass
class Tanque:
    niveis: tuple[int, int, int]
    tempos: tuple[int, int, int] = (6, 8, 10)
    modo: int = MODO_MES
    etapa: int = 0
    nivel_atual: int = 0
    status: int = STATUS_PARADO
    inicio: float | None = None
    receita_ciclo: tuple[tuple[int, int], ...] = ()
    proxima_demo: float | None = None
    vazao: float = 5.0  # Unidades de nível por segundo durante a dosagem.

    def validar_partida(self, *, pelo_mes=True):
        if self.inicio is not None:
            return ExcCodes.DEVICE_BUSY
        # START_CYCLE vindo da rede só vale com o tanque entregue ao MES.
        if pelo_mes and self.modo != MODO_MES:
            return ExcCodes.ILLEGAL_VALUE
        if self.niveis != tuple(sorted(self.niveis)) or not self.niveis[-1]:
            return ExcCodes.ILLEGAL_VALUE
        return None

    def iniciar(self, agora):
        self.inicio = agora
        self.receita_ciclo = tuple(zip(self.niveis, self.tempos))
        self.etapa, self.nivel_atual, self.status = 1, 0, STATUS_EM_CICLO

    def atualizar(self, agora):
        """Etapa n: dosa até NIVELn e depois mistura por TEMPOn segundos."""
        if self.inicio is None:
            return
        decorrido = agora - self.inicio
        nivel_anterior = 0
        for etapa, (nivel, tempo) in enumerate(self.receita_ciclo, start=1):
            dosagem = (nivel - nivel_anterior) / self.vazao
            if decorrido < dosagem:
                self.etapa = etapa
                self.nivel_atual = round(nivel_anterior + decorrido * self.vazao)
                return
            decorrido -= dosagem
            if decorrido < tempo:
                self.etapa, self.nivel_atual = etapa, nivel
                return
            decorrido -= tempo
            nivel_anterior = nivel
        self.etapa, self.nivel_atual, self.status = 0, nivel_anterior, STATUS_CONCLUIDO
        self.inicio = None
        if self.proxima_demo is not None:
            self.proxima_demo = agora + 12

    def registros(self):
        return (
            self.etapa,
            *self.niveis,
            self.nivel_atual,
            *self.tempos,
            self.status,
            self.modo,
        )


def build_mapped_context(*, demo=False, atraso=0, clock=monotonic, modo=None):
    """`modo` inicial dos tanques: 2 (MES) por padrão; 0 (local) na demonstração.

    O registro MODO aceita escrita no simulador para representar a chave
    seletora da planta. O FluidMES nunca escreve nele.
    """
    if modo is None:
        modo = MODO_LOCAL if demo else MODO_MES
    tanques = {
        "TK1": Tanque((15, 30, 50), modo=modo),
        "TK2": Tanque((20, 40, 60), modo=modo),
    }
    if demo:
        agora = clock()
        tanques["TK1"].proxima_demo = agora + atraso + 3
        tanques["TK2"].proxima_demo = agora + atraso + 10

    configuracao = {
        endereco: (tanques[nome], campo)
        for nome, enderecos in ENDERECOS_TANQUES.items()
        for campo, endereco in enderecos.items()
        if campo in CAMPOS_EDITAVEIS or campo == "MODO"
    }
    nomes_por_bobina = {endereco: nome for nome, endereco in BOBINAS_PARTIDA.items()}
    holding = [
        SimData(
            address=endereco,
            values=valor,
            datatype=DataType.UINT16,
            readonly=endereco not in configuracao,
        )
        for nome, enderecos in ENDERECOS_TANQUES.items()
        for endereco, valor in zip(enderecos.values(), tanques[nome].registros())
    ]

    async def operar(funcao, _, endereco, _contagem, registros, valores):
        agora = clock()
        for tanque in tanques.values():
            tanque.atualizar(agora)

        if funcao in (1, 5, 15):
            if valores is not None:
                bobinas = range(endereco, endereco + len(valores))
                if any(bobina not in nomes_por_bobina for bobina in bobinas):
                    return ExcCodes.ILLEGAL_ADDRESS
                partidas = [
                    tanques[nomes_por_bobina[bobina]]
                    for bobina, ligar in zip(bobinas, valores)
                    if ligar
                ]
                for tanque in partidas:
                    if erro := tanque.validar_partida():
                        return erro
                for tanque in partidas:
                    tanque.iniciar(agora)
            elif funcao == 1:
                # Preserva o eco do FC5. Uma leitura FC1 já vê a bobina rearmada.
                registros[0] = 0
            return None

        if funcao not in (3, 6, 16):
            return ExcCodes.ILLEGAL_FUNCTION

        if valores is not None:
            enderecos = range(endereco, endereco + len(valores))
            if any(posicao not in configuracao for posicao in enderecos):
                return ExcCodes.ILLEGAL_ADDRESS
            for posicao, valor in zip(enderecos, valores):
                tanque, campo = configuracao[posicao]
                if campo == "MODO":
                    if valor not in MODOS:
                        return ExcCodes.ILLEGAL_VALUE
                elif tanque.modo != MODO_MES:
                    # Em modo local/aparelho a receita é definida na planta.
                    return ExcCodes.ILLEGAL_VALUE
            for posicao, valor in zip(enderecos, valores):
                tanque, campo = configuracao[posicao]
                if campo == "MODO":
                    tanque.modo = valor
                else:
                    atributo = "niveis" if campo.startswith("NIVEL") else "tempos"
                    indice = int(campo[-1]) - 1
                    parametros = list(getattr(tanque, atributo))
                    parametros[indice] = valor
                    setattr(tanque, atributo, tuple(parametros))
        elif funcao == 3:
            for tanque in tanques.values():
                if (
                    tanque.proxima_demo is not None
                    and agora >= tanque.proxima_demo
                    and tanque.modo != MODO_MES  # Ciclo local, disparado na planta.
                    and tanque.validar_partida(pelo_mes=False) is None
                ):
                    tanque.iniciar(agora)

        for nome, enderecos in ENDERECOS_TANQUES.items():
            for posicao, valor in zip(enderecos.values(), tanques[nome].registros()):
                registros[posicao] = valor
        return None

    return SimDevice(
        id=1,
        simdata=(
            [SimData(address=0, values=[False] * len(BOBINAS_PARTIDA), datatype=DataType.BITS)],
            [SimData(address=0, values=False, datatype=DataType.BITS, readonly=True)],
            holding,
            [SimData(address=0, values=0, datatype=DataType.UINT16, readonly=True)],
        ),
        action=operar,
    )
