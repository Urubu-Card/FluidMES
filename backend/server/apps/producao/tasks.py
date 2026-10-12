from celery import shared_task
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum

from apps.plantas.models import Planta
from apps.producao.models import Pedido, OEERegistro, Parada

TEMPO_PLANEJADO_PADRAO_MIN = 480  # 8h — placeholder até virar config por planta


@shared_task
def calcular_oee_diario():
    ontem = timezone.localdate() - timedelta(days=1)
    for planta in Planta.objects.all():
        _calcular_oee_planta(planta, ontem)


def _calcular_oee_planta(planta, data):
    # 1. tempo parado no dia
    paradas = Parada.objects.filter(planta=planta, inicio__date=data)
    tempo_parado_min = sum(p.duracao_min for p in paradas)

    # 2. pedidos concluídos no dia (aproximação via 'prazo', já que não há data de conclusão)
    pedidos = Pedido.objects.filter(
        planta=planta,
        status=Pedido.Status.CONCLUIDO,
        prazo=data,
    ).select_related('receita')

    quantidade_produzida = pedidos.aggregate(total=Sum('quantidade'))['total'] or 0

    # 3. tempo de ciclo ideal ponderado pela quantidade de cada pedido
    soma_ponderada = sum(p.quantidade * p.receita.tempo1 for p in pedidos)
    tempo_ciclo_ideal_seg = (soma_ponderada / quantidade_produzida) if quantidade_produzida else 0

    # 4. grava o snapshot do dia
    OEERegistro.objects.update_or_create(
        planta=planta,
        data=data,
        defaults={
            'tempo_planejado_min': TEMPO_PLANEJADO_PADRAO_MIN,
            'tempo_parado_min': tempo_parado_min,
            'quantidade_produzida': quantidade_produzida,
            'quantidade_boa': quantidade_produzida,  # sem refugo separado ainda
            'tempo_ciclo_ideal_seg': tempo_ciclo_ideal_seg,
        }
    )