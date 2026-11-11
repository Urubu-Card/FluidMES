import asyncio
import logging
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone
from services.clp_control import Modbus_Control
from apps.plantas.models import Clp, Leitura

logger = logging.getLogger(__name__)


@database_sync_to_async
def load_config():
    return [
        dict(
            id=c.pk,
            ip=c.ip,
            port=c.porta,
            uuid=str(c.planta.uuid),
            nome=c.nome,
            sensors=[
                {
                    "idsensor": s.pk,
                    "tipo_registro": s.tipo_registro,
                    "endereco": s.endereco,
                    "nome": s.nome,
                    "unidade": s.unidade_exibicao,
                }
                for s in c.sensores.all()
            ],
        )
        for c in Clp.objects.filter(ativo=True)
        .select_related("planta")
        .prefetch_related("sensores")
    ]


@database_sync_to_async
def save_readings(clp_id, readings, status):
    changes = {"status": status}
    if status == "online":
        changes["ultima_comunicacao"] = timezone.now()
    Clp.objects.filter(pk=clp_id).update(**changes)
    Leitura.objects.bulk_create(
        [Leitura(sensor_id=sensor_id, valor=value) for sensor_id, value in readings]
    )


class Command(BaseCommand):
    help = "Coleta Modbus somente leitura; recarrega configuração a cada ciclo."

    def add_arguments(self, parser):
        parser.add_argument("--interval", type=float, default=5)

    def handle(self, *args, **options):
        if settings.CHANNEL_LAYERS["default"]["BACKEND"].endswith(
            "InMemoryChannelLayer"
        ):
            raise CommandError(
                "Configure REDIS_URL no coletor e no servidor para telemetria entre processos."
            )
        if options["interval"] < 1:
            raise ValueError("Intervalo mínimo: 1 segundo.")
        try:
            asyncio.run(self.run(options["interval"]))
        except KeyboardInterrupt:
            pass

    async def poll(self, config, semaphore):
        async with semaphore:
            client = Modbus_Control(config["ip"], config["port"])
            readings = []
            error = None
            try:
                await client.Conectar()
                methods = {
                    "coil": client.Ler_Coil,
                    "input_status": client.InputStatus,
                    "holding_register": client.HoldingRegister,
                }
                for sensor in config["sensors"]:
                    values = await methods[sensor["tipo_registro"]](sensor["endereco"])
                    readings.append((sensor["idsensor"], float(values[0])))
            except Exception:
                error = "Falha de comunicação com CLP"
                logger.exception("Falha na coleta do CLP %s", config["id"])
            finally:
                client.conexao.FecharConexao()
            await save_readings(
                config["id"], readings, "offline" if error else "online"
            )
            try:
                await get_channel_layer().group_send(
                    f"plant_{config['uuid']}",
                    {
                        "type": "plant.update",
                        "data": {
                            "clp": config["id"],
                            "nome_clp": config.get("nome"),
                            "leituras": {
                                str(sensor_id): value for sensor_id, value in readings
                            },
                            "sensores": {
                                str(sensor["idsensor"]): {
                                    "nome": sensor.get("nome"),
                                    "unidade": sensor.get("unidade"),
                                }
                                for sensor in config["sensors"]
                            },
                            "erro": error,
                            "timestamp": timezone.now().isoformat(),
                        },
                    },
                )
            except Exception:
                logger.exception("Falha de publicação; leituras preservadas no banco")

    async def run(self, interval):
        semaphore = asyncio.Semaphore(8)
        while True:
            try:
                configs = await load_config()
                results = await asyncio.gather(
                    *(self.poll(config, semaphore) for config in configs),
                    return_exceptions=True,
                )
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(
                            "Falha de persistência/coleta: %s", type(result).__name__
                        )
            except Exception:
                logger.exception("Não foi possível carregar a configuração dos CLPs")
            await asyncio.sleep(interval)
