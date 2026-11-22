"""Ciclo real de ponta a ponta: MES -> Modbus TCP -> CLP simulado."""

import asyncio
import threading
from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from pymodbus.server import ModbusTcpServer
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.accounts.models import Atualizacao, Empresa, Usuarios
from apps.plantas.models import Clp, Planta, Sensor
from services.definir_modo import definir
from services.modbus_simulation import build_mapped_context
from .models import LoteProducao, Pedido, Receita
from .services.execucao_clp import Executor, parametros_clp
from .services.production import reserve
from .services.recipes import snapshot


class SimuladorEmThread:
    """CLP simulado em outra thread, com relógio controlado pelo teste."""

    def __init__(self, modo):
        self.tempo = 1000.0
        self.loop = asyncio.new_event_loop()
        pronto = threading.Event()

        async def servir():
            self.servidor = ModbusTcpServer(
                context=build_mapped_context(clock=lambda: self.tempo, modo=modo),
                address=("127.0.0.1", 0),
            )
            await self.servidor.serve_forever(background=True)
            self.porta = self.servidor.transport.sockets[0].getsockname()[1]
            pronto.set()

        self.thread = threading.Thread(
            target=lambda: (self.loop.run_until_complete(servir()), self.loop.run_forever()),
            daemon=True,
        )
        self.thread.start()
        assert pronto.wait(5)

    def parar(self):
        asyncio.run_coroutine_threadsafe(self.servidor.shutdown(), self.loop).result(5)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(5)


@override_settings(SIMULACAO_PRODUCAO=True)
class ExecucaoClpTests(TestCase):
    def setUp(self):
        self.sim = SimuladorEmThread(modo=0)
        self.addCleanup(self.sim.parar)
        self.executor = Executor()
        self.addCleanup(self.executor.fechar)
        self.agora = timezone.now()
        self.empresa = Empresa.objects.create(nome="Fábrica", cnpj="clp")
        self.preposto = Usuarios.objects.create_user(
            email="p@clp.test", cpf="clp", empresa=self.empresa, role=1
        )
        self.planta = Planta.objects.create(
            nome="Tanque 1", localizacao="Bancada", empresa=self.empresa,
            capacidade_l=50, tempo_reset_seg=0,
        )
        self.clp = Clp.objects.create(
            nome="CLP .43", ip="127.0.0.1", porta=str(self.sim.porta), ativo=True,
            escrita_habilitada=True, planta=self.planta, tanque="TK1", status="",
        )
        self.receita = Receita.objects.create(
            empresa=self.empresa, nome="Fluido", ingrediente1=0, ingrediente2=0,
            ingrediente3=0, tempo1=5, tempo2=0,
            componentes=[
                dict(nome="Base", quantidade_l=20, vazao_l_min=60),
                dict(nome="Aditivo", quantidade_l=30, vazao_l_min=60),
            ],
        )

    def modo(self, valor):
        asyncio.run(definir("127.0.0.1", self.sim.porta, "TK1", valor))

    def tick(self, segundos=0):
        self.sim.tempo += segundos
        self.agora += timedelta(seconds=segundos)
        self.executor.tick(self.agora)
        self.clp.refresh_from_db()
        return self.clp.estado_tanque

    def pedido(self, quantidade):
        pedido = Pedido.objects.create(
            empresa=self.empresa, usuario=self.preposto, planta=self.planta,
            receita=self.receita, receita_snapshot=snapshot(self.receita),
            quantidade=quantidade, prazo=timezone.localdate(), aprovacao="aprovado",
        )
        reserve(pedido, self.agora)
        return pedido

    def lotes(self):
        return list(LoteProducao.objects.order_by("sequencia"))

    def test_recipe_becomes_cumulative_levels_and_mixing_times(self):
        lote = LoteProducao(etapas=[
            dict(tipo="reset", duracao_seg=30),
            dict(tipo="dosagem", quantidade_l=10.4),
            dict(tipo="dosagem", quantidade_l=10.4),
            dict(tipo="mistura", duracao_seg=4.2),
            dict(tipo="dosagem", quantidade_l=5),
            dict(tipo="mistura", duracao_seg=7),
        ])
        self.assertEqual(parametros_clp(lote), ([10, 21, 26], [0, 5, 7]))

    def test_modes_0_and_1_block_the_mes_and_mode_2_runs_the_cycle(self):
        # Modo 0: o MES lê o tanque, mas não programa nem comanda.
        estado = self.tick()
        self.assertEqual((estado["modo"], self.clp.status), (0, "online"))
        self.assertFalse(self.clp.mes_liberado)
        with self.assertRaises(ValidationError):
            self.pedido(50)
        Pedido.objects.all().delete()

        self.modo(2)
        self.tick()
        pedido = self.pedido(100)  # Dois ciclos de 50 L.
        self.assertEqual(len(self.lotes()), 2)

        # Início do pedido: receita gravada e START_CYCLE acionado.
        self.tick()
        self.assertIsNotNone(self.lotes()[0].comando_em)
        estado = self.tick()  # A leitura seguinte confirma o ciclo.
        self.assertEqual(estado["niveis"], [20, 50, 50])
        self.assertEqual(estado["tempos"], [0, 5, 0])
        self.assertEqual(estado["status"], 1)
        primeiro, segundo = self.lotes()
        self.assertEqual((primeiro.status, segundo.status), ("em_andamento", "planejado"))
        self.assertTrue(primeiro.ciclo_confirmado)
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, "em_andamento")
        self.assertTrue(
            Atualizacao.objects.filter(acao="acionou START_CYCLE").exists()
        )

        # Planta vai ao modo 1 no meio do ciclo: o MES só acompanha.
        self.modo(1)
        self.assertEqual(self.tick(8)["etapa"], 2)
        self.assertEqual(self.lotes()[0].status, "em_andamento")
        estado = self.tick(8)  # 10 s de dosagem + 5 s de mistura.
        self.assertEqual((estado["status"], estado["nivel_atual"]), (2, 50))
        primeiro, segundo = self.lotes()
        self.assertEqual((primeiro.status, segundo.status), ("concluido", "planejado"))

        # Segundo ciclo aguarda: nenhuma escrita enquanto o modo não for 2.
        self.tick(5)
        self.tick(5)
        self.assertEqual(self.lotes()[1].status, "planejado")
        self.planta.refresh_from_db()
        self.assertIsNotNone(self.planta.suspensa_desde)
        self.assertEqual(self.clp.estado_tanque["status"], 2)

        self.modo(2)
        self.tick(1)
        self.assertEqual(self.lotes()[1].status, "em_andamento")
        self.tick(1)
        self.tick(15)
        pedido.refresh_from_db()
        self.assertEqual((pedido.status, pedido.quantidade_boa), ("concluido", 100))
        self.planta.refresh_from_db()
        self.assertIsNone(self.planta.suspensa_desde)

    def test_offline_clp_never_concludes_a_cycle(self):
        self.modo(2)
        self.tick()
        self.pedido(50)
        self.tick()
        self.tick(1)
        self.clp.porta = "1"  # Destino sem servidor.
        self.clp.save(update_fields=["porta"])
        self.tick(60)
        self.assertEqual(self.clp.status, "offline")
        self.assertEqual(self.lotes()[0].status, "em_andamento")

    def test_manual_write_is_locked_outside_mes_mode(self):
        api = APIClient()
        api.force_authenticate(self.preposto)
        self.assertEqual(api.post(f"/api/clps/{self.clp.pk}/aplicar_mapeamento/").status_code, 200)
        nivel = Sensor.objects.get(nome="TK1.NIVEL1")
        modo = Sensor.objects.get(nome="TK1.MODO")
        self.assertFalse(modo.gravavel)
        Sensor.objects.filter(pk=modo.pk).update(gravavel=True)

        bloqueado = api.post(f"/api/sensores/{nivel.pk}/escrever/", {"valor": 12}, format="json")
        self.assertEqual(bloqueado.status_code, 423, bloqueado.data)
        self.assertEqual(self.tick()["niveis"][0], 15)
        self.assertEqual(
            api.post(f"/api/sensores/{modo.pk}/escrever/", {"valor": 3}, format="json").status_code,
            403,
        )

        self.modo(2)
        liberado = api.post(f"/api/sensores/{nivel.pk}/escrever/", {"valor": 12}, format="json")
        self.assertEqual(liberado.status_code, 200, liberado.data)
        self.assertEqual(self.tick()["niveis"][0], 12)

        painel = api.get(f"/api/plantas/{self.planta.pk}/").data
        self.assertEqual(api.get("/api/plantas/").data[0]["painel"]["controle"]["modo"], 2)
        self.assertIn("painel", painel)


@override_settings(SIMULACAO_PRODUCAO=True)
class ClpSemTanqueTests(TestCase):
    """Planta com CLP sem tanque não pode ficar pausada por falta de coletor."""

    def setUp(self):
        self.sim = SimuladorEmThread(modo=2)
        self.addCleanup(self.sim.parar)
        self.executor = Executor()
        self.addCleanup(self.executor.fechar)
        empresa = Empresa.objects.create(nome="Fábrica", cnpj="semtk")
        self.preposto = Usuarios.objects.create_user(
            email="p@semtk.test", cpf="semtk", empresa=empresa, role=1
        )
        self.planta = Planta.objects.create(
            nome="Linha", localizacao="Setor", empresa=empresa, tempo_reset_seg=0
        )
        self.api = APIClient()
        self.api.force_authenticate(self.preposto)

    def criar_clp(self, **extra):
        resposta = self.api.post("/api/clps/", {
            "nome": "CLP .43", "ip": "127.0.0.1", "porta": str(self.sim.porta),
            "ativo": True, "planta": self.planta.pk, **extra,
        }, format="json")
        self.assertEqual(resposta.status_code, 201, resposta.data)
        return Clp.objects.get(pk=resposta.data["idclp"])

    def test_clp_without_tank_is_polled_and_plant_stays_available(self):
        from .services.production import availability, motivo_pausa

        clp = self.criar_clp()
        self.assertFalse(clp.sensores.exists())
        self.assertEqual(availability(self.planta, timezone.now()), "CLP sem comunicação")
        self.executor.tick()
        clp.refresh_from_db()
        self.assertEqual(clp.status, "online")
        self.assertEqual(availability(self.planta, timezone.now()), "")
        self.assertEqual(motivo_pausa(self.planta), "")

    def test_production_clp_gets_spreadsheet_tags_on_create(self):
        clp = self.criar_clp(tanque="TK1", escrita_habilitada=True)
        self.assertEqual(clp.sensores.count(), 22)
        self.assertTrue(clp.sensores.filter(nome="TK1.START_CYCLE", gravavel=True).exists())
        self.assertFalse(clp.sensores.get(nome="TK1.MODO").gravavel)
