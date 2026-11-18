"""Execução real dos ciclos pelo CLP (Modbus TCP, mapeamento.xlsx).

Para cada planta cujo CLP tem um tanque (TK1/TK2) definido:

1. lê o bloco do tanque (ETAPA, NIVEL*, TEMPO*, STATUS, MODO);
2. se MODO = 2 (MES) e o tanque está livre, inicia o próximo ciclo programado:
   grava NIVEL1..3 e TEMPO1..3 da receita e aciona START_CYCLE;
3. acompanha o STATUS até o fim do ciclo e conclui o lote.

Com MODO 0 (operação local) ou 1 (aparelho) o MES só lê: nada é escrito e os
ciclos programados aguardam. Todo I/O Modbus acontece fora de transações.
"""

import asyncio
import logging
import math
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from pymodbus.exceptions import ModbusException

from apps.accounts.audit import record
from apps.plantas.models import Clp, Leitura, Planta, Sensor
from services import clp_tanque
from services.clp_control import EscritaRecusada, Modbus_Control
from services.modbus_map import MODO_MES
from ..models import LoteProducao, Pedido

logger = logging.getLogger(__name__)

ERROS_MODBUS = (OSError, ModbusException, IndexError, ValueError)
# O CLP respondeu "não": o ciclo com certeza não começou.
RECUSAS = (
    clp_tanque.MesBloqueado,
    clp_tanque.TanqueOcupado,
    clp_tanque.ParametrosNaoConfirmados,
    EscritaRecusada,
)
ESPERA_APOS_FALHA_SEG = 10
INTERVALO_HISTORICO_SEG = 5


class ReceitaForaDaFaixa(ValueError):
    pass


def parametros_clp(lote):
    """Etapas do lote -> (NIVEL1..3, TEMPO1..3).

    NIVELn é o nível acumulado ao fim da dosagem do ingrediente n; TEMPOn é a
    mistura que acontece logo depois dela. Receita de dois ingredientes repete
    o nível final na terceira etapa, com tempo zero.
    """
    niveis, tempos, nivel = [], [], 0.0
    for etapa in lote.etapas:
        if etapa["tipo"] == "dosagem":
            nivel += etapa["quantidade_l"]
            niveis.append(nivel)
            tempos.append(0.0)
        elif etapa["tipo"] == "mistura" and tempos:
            tempos[-1] += etapa["duracao_seg"]
    if not 1 <= len(niveis) <= 3:
        raise ReceitaForaDaFaixa("O CLP aceita de um a três ingredientes por ciclo.")
    while len(niveis) < 3:
        niveis.append(niveis[-1])
        tempos.append(0.0)
    niveis = [round(v * settings.MODBUS_ESCALA_NIVEL) for v in niveis]
    tempos = [math.ceil(v * settings.MODBUS_ESCALA_TEMPO - 1e-9) for v in tempos]
    if not niveis[-1] or max(niveis + tempos) > 65535:
        raise ReceitaForaDaFaixa(
            f"Receita fora da faixa do CLP (níveis {niveis}, tempos {tempos})."
        )
    return niveis, tempos


def _reprogramar(lotes, cursor):
    """Refaz a previsão dos ciclos que ainda aguardam, em fila a partir de `cursor`."""
    afetados = set()
    for lote in lotes:
        lote.inicio_previsto = cursor
        cursor = lote.fim_previsto = cursor + timedelta(
            seconds=lote.setup_seg + lote.duracao_producao_seg
        )
        lote.save(update_fields=["inicio_previsto", "fim_previsto"])
        afetados.add(lote.pedido_id)
    return afetados


def _descricao(lote, planta):
    return f"Pedido #{lote.pedido_id} · {planta.nome} · {lote.quantidade:g} L"


@transaction.atomic
def decidir(clp_id, estado, agora, pode_tentar=lambda lote_id: True):
    """Atualiza os lotes com a leitura e devolve o comando a enviar, se houver.

    Retorna None, ("rearmar",) ou ("iniciar", lote_id, niveis, tempos, descricao).
    """
    from .production import availability, sync_order
    from ..tasks import _calcular_oee_planta

    clp = Clp.objects.get(pk=clp_id)
    planta = Planta.objects.select_for_update().prefetch_related("clps").get(
        pk=clp.planta_id
    )
    if planta.clp_controle() != clp:
        return None
    lotes = list(
        LoteProducao.objects.select_for_update()
        .filter(planta=planta)
        .exclude(status="concluido")
        .select_related("pedido")
        .order_by("inicio_previsto", "pk")
    )
    atual = next((b for b in lotes if b.status == "em_andamento"), None)
    fila = [b for b in lotes if b.status != "em_andamento"]
    sem_leitura = estado["status"] is None
    em_ciclo = estado["status"] == settings.MODBUS_STATUS_EM_CICLO
    motivo = availability(planta, agora)
    afetados, comando = set(), None

    def suspender(valor):
        if bool(planta.suspensa_desde) != bool(valor):
            planta.suspensa_desde = valor
            planta.save(update_fields=["suspensa_desde"])

    if sem_leitura:
        if lotes:
            suspender(planta.suspensa_desde or agora)
    elif atual and atual.comando_em:
        # START_CYCLE já enviado: o STATUS do CLP conduz o lote.
        if em_ciclo:
            if not atual.ciclo_confirmado:
                atual.ciclo_confirmado = True
                atual.save(update_fields=["ciclo_confirmado"])
        elif atual.ciclo_confirmado:
            atual.status, atual.concluido_em, atual.fim_previsto = "concluido", agora, agora
            atual.save(update_fields=["status", "concluido_em", "fim_previsto"])
            planta.ultima_receita_id = atual.pedido.receita_snapshot["id"]
            planta.ultima_receita_versao = atual.pedido.receita_snapshot["versao"]
            planta.save(update_fields=["ultima_receita", "ultima_receita_versao"])
            record(None, planta.empresa_id, "concluiu", "ciclo no CLP", _descricao(atual, planta))
            _calcular_oee_planta(planta, timezone.localdate(agora))
            afetados |= {atual.pedido_id} | _reprogramar(fila, agora)
            comando = ("rearmar",)
        elif (agora - atual.comando_em).total_seconds() > settings.MODBUS_TIMEOUT_PARTIDA_SEG:
            atual.comando_em = None
            atual.save(update_fields=["comando_em"])
            record(
                None, planta.empresa_id, "não confirmou", "ciclo no CLP",
                f"{_descricao(atual, planta)} · STATUS não indicou ciclo; nova tentativa",
            )
            comando = ("rearmar",)
        suspender(None)
    elif motivo or em_ciclo:
        # Modo 0/1, CLP sem comunicação, parada aberta ou ciclo local em curso.
        if lotes:
            suspender(planta.suspensa_desde or agora)
    else:
        if planta.suspensa_desde:
            suspender(None)
            if atual:
                # A preparação ficou parada durante o bloqueio.
                atual.fim_previsto = max(
                    atual.fim_previsto,
                    agora + timedelta(seconds=atual.duracao_producao_seg),
                )
                atual.save(update_fields=["fim_previsto"])
            afetados |= _reprogramar(fila, atual.fim_previsto if atual else agora)
        if not atual and fila:
            atual, fila = fila[0], fila[1:]
            atual.status, atual.iniciado_em = "em_andamento", agora
            atual.inicio_previsto = agora
            atual.fim_previsto = agora + timedelta(
                seconds=atual.setup_seg + atual.duracao_producao_seg
            )
            atual.save(
                update_fields=["status", "iniciado_em", "inicio_previsto", "fim_previsto"]
            )
            afetados |= {atual.pedido_id} | _reprogramar(fila, atual.fim_previsto)
        # Depois do reset entre receitas (setup), envia a partida.
        if (
            atual
            and (agora - atual.iniciado_em).total_seconds() >= atual.setup_seg
            and pode_tentar(atual.pk)
        ):
            niveis, tempos = parametros_clp(atual)  # Erro aqui desfaz a transação.
            atual.comando_em, atual.ciclo_confirmado = agora, False
            atual.save(update_fields=["comando_em", "ciclo_confirmado"])
            comando = ("iniciar", atual.pk, niveis, tempos, _descricao(atual, planta))

    for pedido in Pedido.objects.filter(pk__in=afetados):
        sync_order(pedido)
    return comando


class Executor:
    """Mantém uma conexão por CLP e conduz os tanques a cada `tick`."""

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.clientes = {}
        self.falhas = {}  # lote -> (instante, mensagem) da última partida recusada
        self.historico = {}  # clp -> instante da última gravação de Leitura

    def fechar(self):
        for cliente in self.clientes.values():
            cliente.conexao.FecharConexao()
        self.clientes.clear()
        self.loop.close()

    def _executar(self, clp, operacao, *args):
        chave = (clp.ip, clp.porta)

        async def chamada():
            cliente = self.clientes.get(chave)
            if cliente is None or not cliente.isConnected():
                cliente = Modbus_Control(clp.ip, clp.porta, retries=0)
                await cliente.Conectar()
                self.clientes[chave] = cliente
            return await operacao(cliente, clp.tanque, *args)

        try:
            return self.loop.run_until_complete(chamada())
        except ERROS_MODBUS:
            if cliente := self.clientes.pop(chave, None):
                cliente.conexao.FecharConexao()
            raise

    def tick(self, agora=None):
        for clp in Clp.objects.filter(ativo=True).select_related("planta"):
            try:
                if clp.tanque:
                    self.processar(clp, agora or timezone.now())
                else:
                    self.monitorar(clp, agora or timezone.now())
            except Exception:
                logger.exception("Falha ao conduzir o CLP %s", clp.pk)

    def monitorar(self, clp, agora):
        """CLP sem tanque: mantém a comunicação em dia (sem Redis) e grava as leituras.

        Sem isso a planta ficaria "sem comunicação" e os pedidos, pausados.
        """
        ultimo = self.historico.get(clp.pk)
        if ultimo and (agora - ultimo).total_seconds() < INTERVALO_HISTORICO_SEG:
            return
        self.historico[clp.pk] = agora
        sensores = list(clp.sensores.all())

        async def ler_todos(cliente, _tanque):
            leitores = {
                "coil": cliente.Ler_Coil,
                "input_status": cliente.InputStatus,
                "holding_register": cliente.HoldingRegister,
            }
            return [
                (s, float((await leitores[s.tipo_registro](s.endereco))[0]))
                for s in sensores
            ]

        try:
            leituras = self._executar(clp, ler_todos)
        except ERROS_MODBUS:
            Clp.objects.filter(pk=clp.pk).update(status="offline")
            return
        Clp.objects.filter(pk=clp.pk).update(status="online", ultima_comunicacao=agora)
        Leitura.objects.bulk_create(Leitura(sensor=s, valor=v) for s, v in leituras)

    def processar(self, clp, agora):
        try:
            estado = self._executar(clp, clp_tanque.ler)
        except ERROS_MODBUS:
            Clp.objects.filter(pk=clp.pk).update(status="offline")
            estado = None
        else:
            estado["lido_em"] = agora.isoformat()
            Clp.objects.filter(pk=clp.pk).update(
                status="online", ultima_comunicacao=agora, estado_tanque=estado
            )
            self._historico(clp, estado, agora)
        if estado is None:
            # Sem leitura não há como comandar; marca a pausa dos ciclos.
            estado = {"status": None}

        def pode_tentar(lote_id):
            falha = self.falhas.get(lote_id)
            return not falha or (agora - falha[0]).total_seconds() >= ESPERA_APOS_FALHA_SEG

        try:
            comando = decidir(clp.pk, estado, agora, pode_tentar)
        except ReceitaForaDaFaixa as erro:
            self._falhou(clp, None, str(erro), agora, chave=("receita", clp.pk))
            return
        if not comando:
            return
        if comando[0] == "rearmar":
            if estado.get("modo") != MODO_MES:
                return  # Fora do modo MES nada é escrito; a próxima partida rearma.
            try:
                self._executar(clp, clp_tanque.rearmar_partida)
            except ERROS_MODBUS + (EscritaRecusada,):
                logger.warning("START_CYCLE do CLP %s não foi rearmado", clp.pk)
            return
        _, lote_id, niveis, tempos, descricao = comando
        try:
            self._executar(clp, clp_tanque.iniciar_ciclo, niveis, tempos)
        except RECUSAS as erro:
            LoteProducao.objects.filter(pk=lote_id).update(comando_em=None)
            self._falhou(clp, descricao, str(erro), agora, chave=lote_id)
        except ERROS_MODBUS:
            # Resultado desconhecido: o STATUS confirma ou o tempo limite repete.
            logger.warning("Partida sem confirmação no CLP %s", clp.pk)
        else:
            self.falhas.pop(lote_id, None)
            record(
                None, clp.planta.empresa_id, "acionou START_CYCLE", "ciclo no CLP",
                f"{descricao} · {clp.tanque} · níveis {niveis} · tempos {tempos}",
            )

    def _falhou(self, clp, descricao, mensagem, agora, *, chave):
        anterior = self.falhas.get(chave)
        self.falhas[chave] = (agora, mensagem)
        if not anterior or anterior[1] != mensagem:
            record(
                None, clp.planta.empresa_id, "teve partida recusada", "ciclo no CLP",
                " · ".join(filter(None, [descricao, mensagem]))[:250],
            )

    def _historico(self, clp, estado, agora):
        """Alimenta os sensores cadastrados pelo mapa da planilha, sem Redis."""
        ultimo = self.historico.get(clp.pk)
        if ultimo and (agora - ultimo).total_seconds() < INTERVALO_HISTORICO_SEG:
            return
        self.historico[clp.pk] = agora
        valores = {
            "ETAPA": estado["etapa"],
            "NIVEL_ATUAL": estado["nivel_atual"],
            "STATUS": estado["status"],
            "MODO": estado["modo"],
            **{f"NIVEL{i}": v for i, v in enumerate(estado["niveis"], 1)},
            **{f"TEMPO{i}": v for i, v in enumerate(estado["tempos"], 1)},
        }
        if estado["start_cycle"] is not None:
            valores["START_CYCLE"] = int(estado["start_cycle"])
        nomes = {f"{clp.tanque}.{campo}": valor for campo, valor in valores.items()}
        Leitura.objects.bulk_create(
            Leitura(sensor=sensor, valor=nomes[sensor.nome])
            for sensor in Sensor.objects.filter(clp=clp, nome__in=nomes)
        )
