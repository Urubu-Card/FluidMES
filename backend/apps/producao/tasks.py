from celery import shared_task
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.db.models import Q
from .models import Pedido, OEERegistro, Parada, LoteProducao
from apps.plantas.models import Planta


@shared_task
def calcular_oee_diario():
    day = timezone.localdate() - timedelta(days=1)
    for plant in Planta.objects.iterator():
        _calcular_oee_planta(plant, day)


def _calcular_oee_planta(planta, data, tempo_planejado=480):
    start = timezone.make_aware(datetime.combine(data, time.min))
    end = start + timedelta(days=1)
    # Clip and merge intervals, including downtime spanning midnight.
    intervals = []
    for stop in Parada.objects.filter(
        Q(fim__gte=start) | Q(fim__isnull=True), planta=planta, inicio__lt=end
    ):
        finish = min(stop.fim or timezone.now(), end)
        begin = max(stop.inicio, start)
        if finish > begin:
            intervals.append((begin, finish))
    merged = []
    for begin, finish in sorted(intervals):
        if merged and begin <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], finish))
        else:
            merged.append((begin, finish))
    downtime = min(
        sum((b - a).total_seconds() / 60 for a, b in merged), tempo_planejado
    )
    orders = list(
        Pedido.objects.filter(
            planta=planta,
            status="concluido",
            concluido_em__gte=start,
            concluido_em__lt=end,
            receita_snapshot={},
        ).select_related("receita")
    )
    total = sum(p.quantidade for p in orders)
    good = sum(p.quantidade_boa or 0 for p in orders)
    lots = list(
        LoteProducao.objects.filter(
            planta=planta,
            status="concluido",
            concluido_em__gte=start,
            concluido_em__lt=end,
        )
    )
    total += sum(b.quantidade for b in lots)
    good += sum(b.quantidade for b in lots)
    cycle = (
        (
            sum(b.duracao_producao_seg for b in lots)
            + sum(
                p.quantidade
                * (
                    p.tempo_ciclo_ideal_seg
                    if p.tempo_ciclo_ideal_seg is not None
                    else p.receita.tempo1 + p.receita.tempo2
                )
                for p in orders
            )
        )
        / total
        if total
        else 0
    )
    record, _ = OEERegistro.objects.update_or_create(
        planta=planta,
        data=data,
        defaults={
            "tempo_planejado_min": tempo_planejado,
            "tempo_parado_min": round(downtime),
            "quantidade_produzida": total,
            "quantidade_boa": good,
            "tempo_ciclo_ideal_seg": cycle,
        },
    )
    return record
