from django.core.management.base import BaseCommand
from apps.plantas.mapeamento import aplicar
from apps.plantas.models import Clp


class Command(BaseCommand):
    help = "Cadastra as 22 tags de mapeamento.xlsx em todos os CLPs (sem duplicar)."

    def handle(self, *args, **options):
        clps = list(Clp.objects.all())
        if not clps:
            self.stdout.write("Nenhum CLP cadastrado. Cadastre em Administração técnica → CLPs.")
        for clp in clps:
            novos, existentes = aplicar(clp)
            self.stdout.write(f"{clp.nome}: {novos} sensores criados, {existentes} já existiam")
