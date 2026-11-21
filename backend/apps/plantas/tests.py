from unittest.mock import AsyncMock, patch
from django.test import TransactionTestCase, override_settings, SimpleTestCase
from .testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models import Empresa, Usuarios
from .models import Planta
from config.asgi import application
from services.clp_control import Modbus_Control


@override_settings(
    CHANNEL_LAYERS={"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
)
class WebsocketTests(TransactionTestCase):
    def setUp(self):
        company = Empresa.objects.create(nome="A", cnpj="A")
        other = Empresa.objects.create(nome="B", cnpj="B")
        self.user = Usuarios.objects.create_user(
            email="ws@example.com",
            password="Test-password-123",
            cpf="A",
            empresa=company,
        )
        self.plant = Planta.objects.create(nome="P", localizacao="A", empresa=company)
        self.foreign = Planta.objects.create(nome="P", localizacao="B", empresa=other)
        self.token = str(RefreshToken.for_user(self.user).access_token)

    async def test_anonymous_is_rejected(self):
        ws = WebsocketCommunicator(
            application,
            f"/ws/plant/{self.plant.uuid}/",
            headers=[(b"origin", b"http://localhost")],
        )
        connected, _ = await ws.connect()
        self.assertFalse(connected)
        await ws.disconnect()

    async def test_cookie_auth_and_foreign_plant(self):
        headers = [
            (b"origin", b"http://localhost"),
            (b"cookie", f"access_token={self.token}".encode()),
        ]
        ws = WebsocketCommunicator(
            application, f"/ws/plant/{self.plant.uuid}/", headers=headers
        )
        connected, _ = await ws.connect()
        self.assertTrue(connected)
        await ws.disconnect()
        ws = WebsocketCommunicator(
            application, f"/ws/plant/{self.foreign.uuid}/", headers=headers
        )
        connected, _ = await ws.connect()
        self.assertFalse(connected)
        await ws.disconnect()

    async def test_bad_origin_is_rejected(self):
        ws = WebsocketCommunicator(
            application,
            f"/ws/plant/{self.plant.uuid}/",
            headers=[
                (b"origin", b"https://evil.example"),
                (b"cookie", f"access_token={self.token}".encode()),
            ],
        )
        connected, _ = await ws.connect()
        self.assertFalse(connected)
        await ws.disconnect()

    async def test_collector_persists_and_broadcasts(self):
        import asyncio
        from channels.db import database_sync_to_async
        from channels.layers import get_channel_layer
        from channels_redis.serializers import MsgPackSerializer
        from services.server_temp import build_context
        from pymodbus.server import ModbusTcpServer
        from apps.plantas.models import Clp, Sensor, Leitura
        from apps.plantas.management.commands.read_plants import Command

        server = ModbusTcpServer(context=build_context(), address=("127.0.0.1", 0))
        await server.serve_forever(background=True)
        port = server.transport.sockets[0].getsockname()[1]
        clp = await database_sync_to_async(Clp.objects.create)(
            nome="Sim", ip="127.0.0.1", porta=str(port), ativo=True, planta=self.plant
        )
        sensor = await database_sync_to_async(Sensor.objects.create)(
            nome="S",
            tipo="volume",
            unidade="litros",
            minimo=0,
            maximo=2000,
            tipo_registro="holding_register",
            endereco=0,
            clp=clp,
        )
        ws = WebsocketCommunicator(
            application,
            f"/ws/plant/{self.plant.uuid}/",
            headers=[
                (b"origin", b"http://localhost"),
                (b"cookie", f"access_token={self.token}".encode()),
            ],
        )
        try:
            connected, _ = await ws.connect()
            self.assertTrue(connected)
            layer = get_channel_layer()
            group_send = layer.group_send
            serializer = MsgPackSerializer()

            async def send_with_redis_format(group, message):
                encoded = serializer.serialize(message)
                await group_send(group, serializer.deserialize(encoded))

            with patch.object(layer, "group_send", side_effect=send_with_redis_format):
                await Command().poll(
                    {
                        "id": clp.pk,
                        "ip": "127.0.0.1",
                        "port": port,
                        "uuid": str(self.plant.uuid),
                        "nome": clp.nome,
                        "sensors": [
                            {
                                "idsensor": sensor.pk,
                                "tipo_registro": "holding_register",
                                "endereco": 0,
                                "nome": sensor.nome,
                                "unidade": sensor.unidade,
                            }
                        ],
                    },
                    asyncio.Semaphore(1),
                )
            data = await ws.receive_json_from()
            self.assertEqual(data["leituras"][str(sensor.pk)], 1000)
            self.assertEqual(data["nome_clp"], clp.nome)
            self.assertEqual(
                data["sensores"][str(sensor.pk)], {"nome": "S", "unidade": "litros"}
            )
            self.assertIsNone(data["erro"])
            self.assertEqual(await database_sync_to_async(Leitura.objects.count)(), 1)
        finally:
            await ws.disconnect()
            await server.shutdown()


class ModbusTests(SimpleTestCase):
    async def test_read_failure_is_not_a_measurement(self):
        client = Modbus_Control("127.0.0.1", 5020)
        with self.assertRaises(ConnectionError):
            await client.HoldingRegister(1)

    async def test_bits_are_trimmed_to_requested_count(self):
        client = Modbus_Control("127.0.0.1", 5020)

        class Response:
            bits = [True, False, False, False, False, False, False, False]

            def isError(self):
                return False

        client.cliente = AsyncMock()
        client.cliente.connected = True
        client.cliente.read_coils.return_value = Response()
        self.assertEqual(await client.Ler_Coil(1, 2), [True, False])

    async def test_real_tcp_simulator(self):
        import asyncio
        from services.server_temp import build_context
        from pymodbus.server import ModbusTcpServer

        server = ModbusTcpServer(context=build_context(), address=("127.0.0.1", 0))
        await server.serve_forever(background=True)
        port = server.transport.sockets[0].getsockname()[1]
        client = Modbus_Control("127.0.0.1", port)
        try:
            await client.Conectar()
            self.assertEqual(await client.HoldingRegister(0, 2), [1000, 1001])
            self.assertEqual(await client.Ler_Coil(0, 2), [False, False])
            self.assertEqual(await client.InputStatus(0, 2), [False, False])
        finally:
            client.conexao.FecharConexao()
            await server.shutdown()


class ProbeTests(SimpleTestCase):
    async def test_tcp_connection_and_modbus_read_are_reported_separately(self):
        from services.clp_probe import probe
        from services.server_temp import build_context
        from pymodbus.server import ModbusTcpServer

        server = ModbusTcpServer(context=build_context(), address=("127.0.0.1", 0))
        await server.serve_forever(background=True)
        port = server.transport.sockets[0].getsockname()[1]
        try:
            connected = await probe("127.0.0.1", port)
            self.assertTrue(connected["conectado"])
            self.assertFalse(connected["leitura_validada"])
            valid = await probe(
                "127.0.0.1",
                port,
                {"nome": "Volume", "tipo_registro": "holding_register", "endereco": 0},
            )
            self.assertTrue(valid["leitura_validada"])
            self.assertEqual(valid["valor"], 1000)
        finally:
            await server.shutdown()


class ProbeApiTests(TransactionTestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        from apps.plantas.models import Clp, Sensor

        self.company = Empresa.objects.create(nome="Probe company", cnpj="probe-api")
        self.owner = Usuarios.objects.create_user(
            email="probe@api.test",
            password="Strong-Probe-891!",
            cpf="probe-api",
            empresa=self.company,
            role=1,
        )
        self.plant = Planta.objects.create(
            nome="Probe tank", localizacao="A", empresa=self.company
        )
        self.clp = Clp.objects.create(
            nome="CLP", ip="127.0.0.1", porta="5020", ativo=True, planta=self.plant
        )
        Sensor.objects.create(
            nome="Volume",
            tipo="volume",
            unidade="litros",
            minimo=0,
            maximo=1000,
            tipo_registro="holding_register",
            endereco=0,
            clp=self.clp,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    def test_successful_probe_updates_verified_communication(self):
        from unittest.mock import patch, AsyncMock

        result = {
            "conectado": True,
            "leitura_validada": True,
            "valor": 1000,
            "sensor": "Volume",
            "mensagem": "OK",
        }
        with patch("services.clp_probe.probe", new=AsyncMock(return_value=result)):
            response = self.client.post(f"/api/clps/{self.clp.pk}/testar/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertTrue(response.data["leitura_validada"])
        self.clp.refresh_from_db()
        self.assertEqual(self.clp.status, "online")
        self.assertIsNotNone(self.clp.ultima_comunicacao)

    def test_employee_and_foreign_device_cannot_be_probed(self):
        from unittest.mock import patch, AsyncMock
        from apps.plantas.models import Clp

        other = Empresa.objects.create(nome="Other", cnpj="probe-other")
        plant = Planta.objects.create(nome="Foreign", localizacao="B", empresa=other)
        device = Clp.objects.create(
            nome="Other", ip="127.0.0.1", porta="5020", ativo=True, planta=plant
        )
        with patch("services.clp_probe.probe", new=AsyncMock()) as probe:
            self.assertEqual(
                self.client.post(f"/api/clps/{device.pk}/testar/").status_code, 404
            )
            self.owner.role = 3
            self.owner.save()
            self.assertEqual(
                self.client.post(f"/api/clps/{self.clp.pk}/testar/").status_code, 403
            )
            probe.assert_not_called()
