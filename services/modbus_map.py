"""Mapa da planilha mapeamento.xlsx, compartilhado entre o simulador e o cadastro."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tag:
    nome: str
    tipo_registro: str
    endereco: int  # Offset Modbus (base zero).

    @property
    def campo(self):
        return self.nome.split(".", 1)[1]

    @property
    def tipo(self):
        if self.campo.startswith("NIVEL"):
            return "nivel"
        if self.campo.startswith("TEMPO"):
            return "tempo"
        return "processo"

    @property
    def gravavel(self):
        return self.campo in CAMPOS_EDITAVEIS or self.campo == "START_CYCLE"


REGISTROS_TANQUE = (
    "ETAPA",
    "NIVEL1",
    "NIVEL2",
    "NIVEL3",
    "NIVEL_ATUAL",
    "TEMPO1",
    "TEMPO2",
    "TEMPO3",
    "STATUS",
    "MODO",
)
ENDERECOS_TANQUES = {
    nome: dict(zip(REGISTROS_TANQUE, range(inicio, inicio + len(REGISTROS_TANQUE))))
    for nome, inicio in (("TK1", 0), ("TK2", 10))
}
# Parâmetros de receita que o MES grava antes de acionar START_CYCLE.
# MODO é escolhido na própria planta; o MES apenas o lê.
CAMPOS_EDITAVEIS = {"NIVEL1", "NIVEL2", "NIVEL3", "TEMPO1", "TEMPO2", "TEMPO3"}

# Registro MODO: quem está no comando do tanque.
MODO_LOCAL, MODO_APARELHO, MODO_MES = 0, 1, 2
MODOS = {
    MODO_LOCAL: "Operação local na planta",
    MODO_APARELHO: "Operação pelo aparelho",
    MODO_MES: "Sistema MES",
}

# Registro STATUS do ciclo.
STATUS_PARADO, STATUS_EM_CICLO, STATUS_CONCLUIDO = 0, 1, 2
STATUS_CICLO = {
    STATUS_PARADO: "Parado",
    STATUS_EM_CICLO: "Em ciclo",
    STATUS_CONCLUIDO: "Ciclo concluído",
}


def modo_label(modo):
    return MODOS.get(modo, f"Modo desconhecido ({modo})")


def tanque_da_tag(nome):
    """TK1/TK2 quando o nome segue a planilha (ex.: TK1.NIVEL1); senão None."""
    prefixo, _, campo = (nome or "").partition(".")
    return prefixo if campo and prefixo in ENDERECOS_TANQUES else None
BOBINAS_PARTIDA = {"TK1": 0, "TK2": 1}
TAGS = tuple(
    tag
    for tanque, enderecos in ENDERECOS_TANQUES.items()
    for tag in (
        *(Tag(f"{tanque}.{campo}", "holding_register", endereco)
          for campo, endereco in enderecos.items()),
        Tag(f"{tanque}.START_CYCLE", "coil", BOBINAS_PARTIDA[tanque]),
    )
)
