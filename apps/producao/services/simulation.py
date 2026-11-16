"""Reconcile the demo clock without a continuously running worker."""

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Empresa
from apps.plantas.models import Planta
from ..models import LoteProducao, Pedido
from ..workflow import advance_plant


@transaction.atomic
def reconcile_company(company_id):
    if not (
        settings.SIMULACAO_PRODUCAO
        and getattr(settings, "SIMULACAO_SOB_DEMANDA", False)
    ):
        return False
    # Serialize simultaneous tabs for this tenant. The plant lock order also
    # matches approvals and reservations, which may run on another instance.
    Empresa.objects.select_for_update().get(pk=company_id)
    active = set(
        LoteProducao.objects.filter(pedido__empresa_id=company_id)
        .exclude(status="concluido")
        .values_list("planta_id", flat=True)
    )
    active.update(
        Pedido.objects.filter(
            empresa_id=company_id,
            receita_snapshot={},
            aprovacao="aprovado",
            status__in=["pendente", "em_andamento"],
        ).values_list("planta_id", flat=True)
    )
    plants = list(
        Planta.objects.select_for_update()
        .filter(empresa_id=company_id, pk__in=active)
        .order_by("pk")
    )
    now = timezone.now()
    for plant in plants:
        advance_plant(plant.pk, now)
    return True
