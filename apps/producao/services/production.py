"""Transactional reservations and simulated batch execution.

Plants whose CLP has a tank (TK1/TK2) run for real through Modbus instead.
"""

from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from rest_framework.exceptions import ValidationError
from apps.plantas.models import Planta
from services.modbus_map import modo_label
from apps.accounts.audit import record
from ..models import Pedido, LoteProducao, Parada
from .planner import Tank, schedule
from .recipes import snapshot


def availability(plant, now):
    clps = [c for c in plant.clps.all() if c.ativo]
    if any(
        c.status != "online"
        or not c.ultima_comunicacao
        or (now - c.ultima_comunicacao).total_seconds() > 15
        for c in clps
    ):
        return "CLP sem comunicação"
    controle = plant.clp_controle(clps)
    if controle:
        if not controle.escrita_habilitada:
            return "Comandos Modbus desabilitados no CLP"
        if not controle.mes_liberado:
            return f"Planta em modo {controle.modo} ({modo_label(controle.modo)}); MES bloqueado"
    if Parada.objects.filter(planta=plant, fim__isnull=True).exists():
        return "Parada aberta"
    return ""


def motivo_pausa(plant, now=None):
    """Explica por que a planta não está produzindo ("" quando está liberada)."""
    from django.conf import settings

    now = now or timezone.now()
    motivo = availability(plant, now)
    if motivo:
        return motivo
    controle = plant.clp_controle()
    if controle and controle.estado_tanque.get("status") == settings.MODBUS_STATUS_EM_CICLO:
        if not plant.lotes.filter(status="em_andamento", comando_em__isnull=False).exists():
            return (
                f"Tanque {controle.tanque} com STATUS {settings.MODBUS_STATUS_EM_CICLO} "
                "(em ciclo) sem pedido do MES: aguardando o ciclo atual terminar"
            )
    if plant.suspensa_desde:
        return "Aguardando a próxima leitura do CLP"
    return ""


def preview(
    company_id, recipe, quantity, preferred_id=None, now=None, recipe_snapshot=None
):
    now = now or timezone.now()
    data = recipe_snapshot or snapshot(recipe)
    plants = list(Planta.objects.filter(empresa_id=company_id).prefetch_related("clps"))
    future = list(
        LoteProducao.objects.filter(planta__empresa_id=company_id)
        .exclude(status="concluido")
        .select_related("pedido")
        .order_by("fim_previsto")
    )
    latest = {b.planta_id: b for b in future}
    legacy = list(
        Pedido.objects.filter(
            empresa_id=company_id, aprovacao="aprovado", receita_snapshot={}
        )
        .exclude(status__in=["concluido", "cancelado"])
        .select_related("receita")
    )
    tanks = []
    for plant in plants:
        if availability(plant, now):
            continue
        last = latest.get(plant.pk)
        ready = max(0, (last.fim_previsto - now).total_seconds()) if last else 0
        previous = (
            last.pedido.receita_snapshot
            if last
            else dict(id=plant.ultima_receita_id, versao=plant.ultima_receita_versao)
        )
        for old in [o for o in legacy if o.planta_id == plant.pk]:
            ready += max(
                0,
                old.duracao_simulada_seg
                - ((now - old.iniciado_em).total_seconds() if old.iniciado_em else 0),
            )
            previous = dict(id=old.receita_id, versao=old.receita.versao)
        change = previous.get("id") and (
            previous.get("id"),
            previous.get("versao"),
        ) != (data["id"], data["versao"])
        tanks.append(
            Tank(
                plant.pk,
                plant.nome,
                plant.capacidade_l,
                ready,
                plant.tempo_reset_seg if change else 0,
                plant.pk == preferred_id,
                (
                    "Tanque inicialmente preparado; sem reset inicial."
                    if not previous.get("id")
                    else (
                        f"Troca de receita: reset de {plant.tempo_reset_seg:g} s."
                        if change
                        else "Repete a mesma versão da receita sem reset."
                    )
                ),
            )
        )
    try:
        plan = schedule(data, float(quantity), tanks)
    except ValueError as error:
        raise ValidationError(str(error))
    plan["plantas"] = sorted({b["planta_nome"] for b in plan["lotes"]})
    plan["receita_nome"], plan["receita_versao"] = data["nome"], data["versao"]
    for batch in plan["lotes"]:
        batch["inicio_previsto"] = (
            now + timedelta(seconds=batch.pop("inicio_seg"))
        ).isoformat()
        batch["fim_previsto"] = (
            now + timedelta(seconds=batch.pop("fim_seg"))
        ).isoformat()
    plan["previsao_conclusao"] = max(b["fim_previsto"] for b in plan["lotes"])
    plan["gerado_em"] = now.isoformat()
    return plan


@transaction.atomic
def reserve(order, now=None):
    now = now or timezone.now()
    # Consistent lock order across approval and creation; reserve all company tanks.
    list(
        Planta.objects.select_for_update()
        .filter(empresa_id=order.empresa_id)
        .order_by("pk")
    )
    if order.lotes.exists():
        raise ValidationError("Este pedido já possui programação.")
    plan = preview(
        order.empresa_id,
        order.receita,
        order.quantidade,
        order.planta_preferida_id,
        now,
        order.receita_snapshot,
    )
    batches = [
        LoteProducao(
            pedido=order,
            planta_id=batch["planta"],
            sequencia=index,
            quantidade=batch["quantidade"],
            inicio_previsto=batch["inicio_previsto"],
            fim_previsto=batch["fim_previsto"],
            setup_seg=batch["setup_seg"],
            duracao_producao_seg=batch["duracao_producao_seg"],
            etapas=batch["etapas"],
        )
        for index, batch in enumerate(plan["lotes"], 1)
    ]
    LoteProducao.objects.bulk_create(batches)
    order.plano_snapshot = {k: v for k, v in plan.items() if k != "lotes"}
    order.plano_snapshot["plantas"] = sorted({b["planta_nome"] for b in plan["lotes"]})
    order.save(update_fields=["plano_snapshot"])
    if settings.SIMULACAO_PRODUCAO:
        for plant_id in sorted({b["planta"] for b in plan["lotes"]}):
            advance_batches(plant_id, now)


def sync_order(order):
    batches = list(order.lotes.all())
    started = [b.iniciado_em for b in batches if b.iniciado_em]
    order.iniciado_em = min(started) if started else None
    order.status = (
        "concluido"
        if all(b.status == "concluido" for b in batches)
        else "em_andamento" if started else "pendente"
    )
    order.quantidade_boa = sum(b.quantidade for b in batches if b.status == "concluido")
    order.concluido_em = (
        max(b.concluido_em for b in batches) if order.status == "concluido" else None
    )
    order.plano_snapshot = {
        **order.plano_snapshot,
        "previsao_conclusao": max(b.fim_previsto for b in batches).isoformat(),
    }
    order.save(
        update_fields=[
            "status",
            "iniciado_em",
            "concluido_em",
            "quantidade_boa",
            "plano_snapshot",
        ]
    )


@transaction.atomic
def advance_batches(plant_id, now=None):
    if not settings.SIMULACAO_PRODUCAO:
        return
    now = now or timezone.now()
    plant = Planta.objects.select_for_update().prefetch_related("clps").get(pk=plant_id)
    if plant.clp_controle():
        return  # Execução real: conduzida pelo CLP em services/execucao_clp.py.
    if availability(plant, now):
        if not plant.suspensa_desde:
            plant.suspensa_desde = now
            plant.save(update_fields=["suspensa_desde"])
        return
    batches = list(
        LoteProducao.objects.select_for_update()
        .filter(planta=plant)
        .exclude(status="concluido")
        .select_related("pedido")
        .order_by("inicio_previsto", "pk")
    )
    affected = set()
    if plant.suspensa_desde:
        if batches:
            delay = max(
                0,
                (
                    now - max(plant.suspensa_desde, batches[0].inicio_previsto)
                ).total_seconds(),
            )
            for batch in batches:
                batch.fim_previsto += timedelta(seconds=delay)
                if batch.iniciado_em:
                    batch.pausa_acumulada_seg += delay
                else:
                    batch.inicio_previsto += timedelta(seconds=delay)
                batch.save(
                    update_fields=[
                        "inicio_previsto",
                        "fim_previsto",
                        "pausa_acumulada_seg",
                    ]
                )
                affected.add(batch.pedido_id)
        plant.suspensa_desde = None
        plant.save(update_fields=["suspensa_desde"])
    for batch in batches:
        if batch.inicio_previsto > now:
            break
        if not batch.iniciado_em:
            batch.iniciado_em = batch.inicio_previsto
            batch.status = "em_andamento"
            batch.save(update_fields=["iniciado_em", "status"])
            record(
                None,
                plant.empresa_id,
                "iniciou",
                "ciclo simulado",
                f"Pedido #{batch.pedido_id} · {plant.nome} · {batch.quantidade:g} L",
            )
        affected.add(batch.pedido_id)
        if batch.fim_previsto > now:
            break
        batch.status = "concluido"
        batch.concluido_em = batch.fim_previsto
        batch.save(update_fields=["status", "concluido_em"])
        plant.ultima_receita_id = batch.pedido.receita_snapshot["id"]
        plant.ultima_receita_versao = batch.pedido.receita_snapshot["versao"]
        plant.save(update_fields=["ultima_receita", "ultima_receita_versao"])
        record(
            None,
            plant.empresa_id,
            "concluiu",
            "ciclo simulado",
            f"Pedido #{batch.pedido_id} · {plant.nome} · {batch.quantidade:g} L",
        )
        from ..tasks import _calcular_oee_planta

        _calcular_oee_planta(plant, timezone.localdate(batch.concluido_em))
    for order in Pedido.objects.filter(pk__in=affected):
        sync_order(order)
