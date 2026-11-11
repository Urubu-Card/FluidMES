from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.plantas.models import Planta
from apps.producao.models import LoteProducao
from apps.producao.services.production import motivo_pausa


class Command(BaseCommand):
    help = "Mostra, por planta, o estado do CLP e por que a produção está (ou não) pausada."

    def handle(self, *args, **options):
        for p in Planta.objects.prefetch_related("clps"):
            self.stdout.write(f"\n== {p.nome} | situação: {motivo_pausa(p, timezone.now()) or 'liberada'}")
            for c in p.clps.all():
                e = c.estado_tanque or {}
                self.stdout.write(
                    f"  CLP {c.nome} {c.ip}:{c.porta} | ativo: {c.ativo} | comandos: {c.escrita_habilitada}"
                    f" | tanque: {c.tanque or '-'} | comunicação: {c.status} {c.ultima_comunicacao}"
                )
                if c.tanque:
                    self.stdout.write(
                        f"    MODO: {e.get('modo')} | STATUS: {e.get('status')} | ETAPA: {e.get('etapa')}"
                        f" | NÍVEL: {e.get('nivel_atual')} | START_CYCLE: {e.get('start_cycle')}"
                    )
            for l in LoteProducao.objects.filter(planta=p).exclude(status="concluido"):
                self.stdout.write(
                    f"  ciclo do pedido #{l.pedido_id} | {l.status} | partida enviada: {l.comando_em}"
                    f" | confirmado: {l.ciclo_confirmado}"
                )
