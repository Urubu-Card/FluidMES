from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.plantas.models import Leitura


class Command(BaseCommand):
    help = "Remove em lotes leituras antigas; padrão apenas informa a quantidade."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=90)
        parser.add_argument("--execute", action="store_true")

    def handle(self, *args, **options):
        if options["days"] < 1:
            raise ValueError("Informe pelo menos um dia.")
        query = Leitura.objects.filter(
            timestamp__lt=timezone.now() - timedelta(days=options["days"])
        )
        self.stdout.write(f"{query.count()} leituras elegíveis.")
        if options["execute"]:
            while ids := list(query.values_list("pk", flat=True)[:1000]):
                Leitura.objects.filter(pk__in=ids).delete()
