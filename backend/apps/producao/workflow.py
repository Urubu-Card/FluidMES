"""Transactional approvals and one persistent simulation queue per plant."""

from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.accounts.audit import record
from apps.plantas.models import Planta
from .models import Pedido, Solicitacao


@transaction.atomic
def advance_plant(plant_id, now=None):
    now = now or timezone.now()
    from .services.production import advance_batches

    advance_batches(plant_id, now)
    plant = Planta.objects.select_for_update().get(pk=plant_id)
    running = (
        Pedido.objects.select_for_update()
        .filter(planta=plant, status="em_andamento", receita_snapshot={})
        .order_by("iniciado_em", "pk")
        .first()
    )
    if running:
        # Legacy running orders get a start time instead of becoming stuck.
        if not running.iniciado_em:
            running.iniciado_em = now
            running.save(update_fields=["iniciado_em"])
        end = running.iniciado_em + timedelta(seconds=running.duracao_simulada_seg)
        if end > now:
            return
        running.status = "concluido"
        running.concluido_em = end
        running.quantidade_boa = running.quantidade
        running.save(update_fields=["status", "concluido_em", "quantidade_boa"])
        from .tasks import _calcular_oee_planta

        _calcular_oee_planta(plant, timezone.localdate(end))
        record(
            None,
            plant.empresa_id,
            "concluiu",
            "produção simulada",
            f"Pedido #{running.pk} · {plant.nome}",
        )
    if settings.SIMULACAO_PRODUCAO:
        queued = (
            Pedido.objects.select_for_update()
            .filter(
                planta=plant,
                status="pendente",
                aprovacao="aprovado",
                receita_snapshot={},
            )
            .select_related("receita")
            .order_by("aprovado_em", "pk")
            .first()
        )
        if queued:
            queued.status = "em_andamento"
            queued.iniciado_em = now
            queued.tempo_ciclo_ideal_seg = queued.receita.tempo1 + queued.receita.tempo2
            queued.save(
                update_fields=["status", "iniciado_em", "tempo_ciclo_ideal_seg"]
            )
            record(
                None,
                plant.empresa_id,
                "iniciou",
                "produção simulada",
                f"Pedido #{queued.pk} · {plant.nome}",
            )


@transaction.atomic
def decide_order(order_id, actor, approved):
    # All operations take locks in plant -> order order to avoid deadlocks.
    snapshot = Pedido.objects.get(pk=order_id, empresa_id=actor.empresa_id)
    list(
        Planta.objects.select_for_update()
        .filter(empresa_id=actor.empresa_id)
        .order_by("pk")
    )
    order = Pedido.objects.select_for_update().get(pk=order_id)
    if order.status != "pendente" or order.aprovacao != "aguardando":
        raise ValidationError("Este pedido já foi analisado.")
    order.aprovacao = "aprovado" if approved else "reprovado"
    order.aprovado_por = actor
    order.aprovado_em = timezone.now()
    if not approved:
        order.status = "cancelado"
    order.save(update_fields=["aprovacao", "aprovado_por", "aprovado_em", "status"])
    record(
        actor,
        actor.empresa_id,
        "aprovou" if approved else "recusou",
        "pedido de produção",
        f"Pedido #{order.pk} · {order.receita.nome}",
    )
    if approved:
        if order.receita_snapshot:
            from .services.production import reserve

            reserve(order)
        elif settings.SIMULACAO_PRODUCAO:
            advance_plant(order.planta_id)
    order.refresh_from_db()
    return order


@transaction.atomic
def decide_request(request_id, actor, approved):
    req = Solicitacao.objects.select_for_update().get(
        pk=request_id, empresa_id=actor.empresa_id
    )
    if req.status != "aguardando":
        raise ValidationError("Esta solicitação já foi analisada.")
    if approved:
        from apps.plantas.serializers import PlantaSerializer
        from .serializers import ReceitaSerializer

        serializer = (PlantaSerializer if req.tipo == "planta" else ReceitaSerializer)(
            data=req.dados
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(empresa=actor.empresa)
        req.resultado_id = instance.pk
        record(
            actor,
            actor.empresa_id,
            "criou",
            req.tipo,
            f"{instance.nome} · solicitação #{req.pk}",
        )
    req.status = "aprovado" if approved else "reprovado"
    req.decidido_por = actor
    req.decidido_em = timezone.now()
    req.save(update_fields=["resultado_id", "status", "decidido_por", "decidido_em"])
    record(
        actor,
        actor.empresa_id,
        "aprovou" if approved else "recusou",
        f"solicitação de {req.tipo}",
        req.dados.get("nome", ""),
    )
    return req


def enqueue_request(request, kind, serializer):
    from rest_framework.response import Response

    with transaction.atomic():
        req = Solicitacao.objects.create(
            empresa=request.user.empresa,
            autor=request.user,
            tipo=kind,
            dados=serializer.validated_data,
        )
        record(
            request.user,
            request.user.empresa_id,
            "solicitou",
            kind,
            req.dados.get("nome", ""),
        )
    return Response(
        {"detail": "Solicitação enviada para aprovação.", "solicitacao_id": req.pk},
        status=202,
    )
