from django.test import SimpleTestCase, TestCase
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.constants import ExcCodes
from pymodbus.server import ModbusTcpServer
from rest_framework.test import APIClient

from apps.accounts.models import Atualizacao, Empresa, Usuarios
from services.modbus_map import TAGS
from services.modbus_simulation import build_mapped_context
from .models import Clp, Planta, Sensor


class MappedSimulatorTests(SimpleTestCase):
    async def test_cycles_and_writes_over_tcp(self):
        time = 100.0
        servers = []
        clients = []
        try:
            for _ in range(2):
                server = ModbusTcpServer(
                    context=build_mapped_context(clock=lambda: time),
                    address=("127.0.0.1", 0),
                )
                servers.append(server)
                await server.serve_forever(background=True)
                port = server.transport.sockets[0].getsockname()[1]
                client = AsyncModbusTcpClient("127.0.0.1", port=port)
                clients.append(client)
                self.assertTrue(await client.connect())

            first, second = clients
            result = await first.read_holding_registers(0, count=20)
            self.assertEqual(
                result.registers,
                [0, 15, 30, 50, 0, 6, 8, 10, 0, 2,
                 0, 20, 40, 60, 0, 6, 8, 10, 0, 2],
            )
            invalid = await first.write_registers(3, [55, 100])
            self.assertEqual(invalid.exception_code, ExcCodes.ILLEGAL_ADDRESS)
            self.assertEqual((await first.read_holding_registers(3)).registers, [50])
            self.assertEqual(
                (await first.write_coil(2, True)).exception_code,
                ExcCodes.ILLEGAL_ADDRESS,
            )
            # Modo inexistente é recusado; 0 e 1 tiram o tanque do MES.
            self.assertEqual(
                (await first.write_register(9, 3)).exception_code,
                ExcCodes.ILLEGAL_VALUE,
            )
            for modo in (0, 1):
                self.assertFalse((await first.write_register(19, modo)).isError())
                self.assertEqual(
                    (await first.write_coil(1, True)).exception_code,
                    ExcCodes.ILLEGAL_VALUE,
                )
                self.assertEqual(
                    (await first.write_register(11, 25)).exception_code,
                    ExcCodes.ILLEGAL_VALUE,
                )
            self.assertEqual(
                (await first.read_holding_registers(10, count=2)).registers, [0, 20]
            )

            start = await first.write_coil(0, True)
            self.assertFalse(start.isError())
            self.assertTrue(start.bits[0])
            self.assertEqual((await first.read_coils(0, count=2)).bits[:2], [False, False])
            self.assertEqual(
                (await first.write_coil(0, True)).exception_code, ExcCodes.DEVICE_BUSY
            )
            # A receita do ciclo em curso é a do instante da partida.
            self.assertFalse((await first.write_register(3, 55)).isError())

            # Etapa 1: dosa 15 em 3 s e mistura 6 s. Etapa 2 começa em 9 s.
            time += 10
            values = (await first.read_holding_registers(0, count=10)).registers
            self.assertEqual((values[0], values[4], values[8]), (2, 20, 1))
            self.assertEqual((await second.read_holding_registers(8)).registers, [0])

            # Total: 50 / 5 de dosagem + 24 s de mistura = 34 s.
            time += 23
            values = (await first.read_holding_registers(0, count=10)).registers
            self.assertEqual((values[0], values[4], values[8]), (3, 50, 1))
            time += 2
            values = (await first.read_holding_registers(0, count=10)).registers
            self.assertEqual((values[0], values[3], values[4], values[8]), (0, 55, 50, 2))

            self.assertFalse((await first.write_register(19, 2)).isError())
            self.assertFalse((await first.write_coils(0, [True, True])).isError())
            self.assertEqual((await first.read_holding_registers(18)).registers, [1])
            self.assertEqual((await second.read_holding_registers(18)).registers, [0])
        finally:
            for client in clients:
                client.close()
            for server in servers:
                await server.shutdown()


class MappingApiTests(TestCase):
    def setUp(self):
        self.company = Empresa.objects.create(nome="Empresa A", cnpj="A")
        self.owner = Usuarios.objects.create_user(
            email="preposto@empresa.test", cpf="A", empresa=self.company, role=1
        )
        self.clp = self.make_clp(self.company)
        self.client = APIClient()
        self.client.force_authenticate(self.owner)

    def make_clp(self, company):
        plant = Planta.objects.create(nome="Linha", localizacao="Setor", empresa=company)
        return Clp.objects.create(
            nome="CLP",
            ip="127.0.0.1",
            porta="5020",
            ativo=True,
            planta=plant,
        )

    def apply(self, clp):
        return self.client.post(f"/api/clps/{clp.pk}/aplicar_mapeamento/")

    def test_registers_all_tags_and_preserves_existing_configuration(self):
        response = self.apply(self.clp)
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data, {"cadastradas": 22, "existentes": 0})
        self.assertEqual(
            set(self.clp.sensores.values_list("nome", "tipo_registro", "endereco")),
            {(tag.nome, tag.tipo_registro, tag.endereco) for tag in TAGS},
        )
        self.clp.sensores.filter(nome="TK2.NIVEL_ATUAL").update(unidade="litros")
        self.assertEqual(self.apply(self.clp).data, {"cadastradas": 0, "existentes": 22})
        self.assertEqual(self.clp.sensores.get(nome="TK2.NIVEL_ATUAL").unidade, "litros")
        self.assertEqual(Atualizacao.objects.filter(empresa=self.company).count(), 1)

    def test_conflict_leaves_other_tags_and_audit_untouched(self):
        Sensor.objects.create(
            nome="Sensor antigo",
            clp=self.clp,
            tipo=Sensor.Tipo.VOLUME,
            unidade="litros",
            minimo=0,
            maximo=100,
            tipo_registro=Sensor.TipoRegistro.HOLDING_REGISTER,
            endereco=4,
        )
        response = self.apply(self.clp)
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(self.clp.sensores.count(), 1)
        self.assertFalse(Atualizacao.objects.filter(empresa=self.company).exists())

    def test_rejects_cross_company_access_and_non_owner(self):
        foreign = self.make_clp(Empresa.objects.create(nome="Empresa B", cnpj="B"))
        self.assertEqual(self.apply(foreign).status_code, 404)
        self.owner.role = 3
        self.owner.save(update_fields=["role"])
        self.assertEqual(self.apply(self.clp).status_code, 403)
        self.assertFalse(Sensor.objects.exists())
