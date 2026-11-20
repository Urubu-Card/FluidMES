from datetime import date
from django.core.management.base import BaseCommand
from apps.plantas.models import Planta
from apps.producao.tasks import _calcular_oee_planta


class Command(BaseCommand):
    help = (
        "Recalcula OEE idempotente de um dia (tempos das receitas em segundos/unidade)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--date", type=date.fromisoformat, required=True)
        parser.add_argument("--planned-minutes", type=int, default=480)

    def handle(self, *args, **options):
        if options["planned_minutes"] <= 0:
            raise ValueError("Tempo planejado deve ser positivo.")
        for plant in Planta.objects.iterator():
            _calcular_oee_planta(plant, options["date"], options["planned_minutes"])
        self.stdout.write("OEE calculado.")
