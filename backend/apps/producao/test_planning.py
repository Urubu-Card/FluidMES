from datetime import timedelta
from unittest import TestCase as PureTestCase
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from apps.accounts.models import Empresa, Usuarios
from apps.plantas.models import Planta
from .models import Receita, Pedido, LoteProducao, Parada
from .services.planner import Tank, schedule
from .services.recipes import stages
from .services.production import advance_batches

RECIPE = dict(
    id=1,
    nome="Guaraná",
    versao=1,
    componentes=[
        dict(nome="Água", quantidade_l=40, vazao_l_min=60),
        dict(nome="Xarope", quantidade_l=10, vazao_l_min=60),
    ],
    mistura1_seg=30,
    mistura2_seg=0,
)


class PlannerTests(PureTestCase):
    def test_four_parallel_tanks_finish_200_litres_in_one_cycle(self):
        plan = schedule(RECIPE, 200, [Tank(i, str(i), 50) for i in range(4)])
        self.assertEqual(plan["lotes_qtd"], 4)
        self.assertAlmostEqual(plan["duracao_total_seg"], 80, places=4)
        self.assertAlmostEqual(sum(b["quantidade"] for b in plan["lotes"]), 200)

    def test_one_tank_repeats_four_cycles_without_extra_reset(self):
        plan = schedule(RECIPE, 200, [Tank(1, "A", 50, setup=20)])
        self.assertEqual(plan["lotes_qtd"], 4)
        self.assertAlmostEqual(plan["duracao_total_seg"], 340, places=4)
        self.assertEqual([b["setup_seg"] for b in plan["lotes"]], [20, 0, 0, 0])

    def test_waiting_for_another_tank_can_finish_earlier(self):
        alone = schedule(RECIPE, 200, [Tank(1, "A", 50)])
        split = schedule(RECIPE, 200, [Tank(1, "A", 50), Tank(2, "B", 50, ready=20)])
        self.assertLess(split["duracao_total_seg"], alone["duracao_total_seg"])
        self.assertEqual(split["plantas_qtd"], 2)

    def test_same_recipe_affinity_can_beat_free_tank_with_reset(self):
        plan = schedule(
            RECIPE, 50, [Tank(1, "A", 50, ready=10), Tank(2, "B", 50, setup=80)]
        )
        self.assertEqual(plan["plantas_qtd"], 1)
        self.assertEqual(plan["lotes"][0]["planta"], 1)

    def test_preference_does_not_override_faster_completion(self):
        plan = schedule(
            RECIPE, 50, [Tank(1, "A", 50, ready=1000, preferred=True), Tank(2, "B", 50)]
        )
        self.assertEqual(plan["lotes"][0]["planta"], 2)

    def test_partial_batches_do_not_overfill_and_preserve_volume(self):
        plan = schedule(RECIPE, 123.45, [Tank(1, "A", 50), Tank(2, "B", 35)])
        self.assertAlmostEqual(
            sum(b["quantidade"] for b in plan["lotes"]), 123.45, places=5
        )
        self.assertTrue(
            all(
                b["quantidade"] <= (50 if b["planta"] == 1 else 35)
                for b in plan["lotes"]
            )
        )

    def test_mixing_is_fixed_but_dosing_scales_with_volume(self):
        small = stages(RECIPE, 100)
        large = stages(RECIPE, 200)
        self.assertEqual(small[-1]["duracao_seg"], large[-1]["duracao_seg"])
        self.assertEqual(large[0]["duracao_seg"], small[0]["duracao_seg"] * 2)

    def test_three_ingredients_have_two_mixes_in_the_right_order(self):
        recipe = {
            **RECIPE,
            "componentes": RECIPE["componentes"]
            + [dict(nome="Corante", quantidade_l=1, vazao_l_min=30)],
            "mistura2_seg": 10,
        }
        self.assertEqual(
            [s["tipo"] for s in stages(recipe, 51)],
            ["dosagem", "dosagem", "mistura", "dosagem", "mistura"],
        )

    def test_extremely_slow_flow_is_rejected_before_datetime_overflow(self):
        slow = {
            **RECIPE,
            "componentes": [
                {**p, "vazao_l_min": 0.000001} for p in RECIPE["componentes"]
            ],
        }
        with self.assertRaises(ValueError):
            schedule(slow, 200, [Tank(1, "A", 50)])

    def test_invalid_or_unavailable_capacity_cannot_form_a_plan(self):
        for quantity, tanks in [
            (0, [Tank(1, "A", 50)]),
            (10, []),
            (float("nan"), [Tank(1, "A", 50)]),
        ]:
            with self.assertRaises(ValueError):
                schedule(RECIPE, quantity, tanks)


class ProductionPlanTests(TestCase):
    def setUp(self):
        self.company = Empresa.objects.create(nome="MES", cnpj="planning")
        self.owner = Usuarios.objects.create_user(
            email="owner@plan.test",
            password="Strong-Plan-232!",
            cpf="planning",
            empresa=self.company,
            role=1,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.owner)
        self.plants = [
            Planta.objects.create(
                nome=f"Tanque {i}",
                localizacao="A",
                empresa=self.company,
                capacidade_l=50,
                tempo_reset_seg=20,
            )
            for i in range(4)
        ]
        self.recipe = self.client.post(
            "/api/receitas/",
            {
                "nome": "Guaraná",
                "componentes": RECIPE["componentes"],
                "tempo1": 30,
                "tempo2": 0,
            },
            format="json",
        ).data

    def payload(self):
        return dict(
            receita=self.recipe["idreceita"], quantidade=200, prazo="2027-01-01"
        )

    def test_preview_is_read_only_and_checks_tenant(self):
        response = self.client.post("/api/pedidos/prever/", self.payload())
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["plantas_qtd"], 4)
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertEqual(LoteProducao.objects.count(), 0)
        other = Empresa.objects.create(nome="Other", cnpj="plan-other")
        foreign = Planta.objects.create(nome="Foreign", localizacao="B", empresa=other)
        self.assertEqual(
            self.client.post(
                "/api/pedidos/prever/", {**self.payload(), "planta": foreign.pk}
            ).status_code,
            400,
        )

    def test_order_finishes_only_after_every_tank_and_oee_counts_its_own_volume(self):
        response = self.client.post("/api/pedidos/", self.payload())
        self.assertEqual(response.status_code, 201, response.data)
        order = Pedido.objects.get(pk=response.data["idpedido"])
        self.assertEqual(order.lotes.count(), 4)
        end = order.lotes.latest("fim_previsto").fim_previsto + timedelta(seconds=1)
        for plant in self.plants[:-1]:
            advance_batches(plant.pk, end)
        order.refresh_from_db()
        self.assertEqual(order.status, "em_andamento")
        advance_batches(self.plants[-1].pk, end)
        order.refresh_from_db()
        self.assertEqual(order.status, "concluido")
        self.assertAlmostEqual(order.quantidade_boa, 200)
        cards = self.client.get("/api/plantas/").data
        self.assertTrue(
            all(
                abs(card["painel"]["quantidade_produzida"] - 50) < 1e-5
                for card in cards
            )
        )
        self.assertTrue(
            all(
                abs(p.oee_registros.get().quantidade_produzida - 50) < 1e-5
                for p in self.plants
            )
        )

    def test_recipe_edit_preserves_approved_snapshot(self):
        response = self.client.post("/api/pedidos/", self.payload())
        order = Pedido.objects.get(pk=response.data["idpedido"])
        before = order.receita_snapshot
        update = self.client.patch(
            f"/api/receitas/{self.recipe['idreceita']}/", {"tempo1": 500}, format="json"
        )
        self.assertEqual(update.status_code, 200, update.data)
        self.assertEqual(update.data["versao"], 2)
        order.refresh_from_db()
        self.assertEqual(order.receita_snapshot, before)

    def test_reservations_on_each_tank_never_overlap(self):
        self.client.post("/api/pedidos/", self.payload())
        self.client.post("/api/pedidos/", self.payload())
        for plant in self.plants:
            batches = list(plant.lotes.order_by("inicio_previsto"))
            for first, second in zip(batches, batches[1:]):
                self.assertLessEqual(first.fim_previsto, second.inicio_previsto)

    def test_worker_order_is_not_reserved_until_chief_approval(self):
        self.owner.role = 3
        self.owner.save()
        response = self.client.post("/api/pedidos/", self.payload())
        order = Pedido.objects.get(pk=response.data["idpedido"])
        self.assertEqual(order.lotes.count(), 0)
        self.assertEqual(
            self.client.post(f"/api/pedidos/{order.pk}/aprovar/").status_code, 403
        )
        self.owner.role = 2
        self.owner.save()
        result = self.client.post(f"/api/pedidos/{order.pk}/aprovar/")
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(order.lotes.count(), 4)
        self.assertEqual(
            self.client.post(f"/api/pedidos/{order.pk}/aprovar/").status_code, 400
        )

    def test_plant_cannot_shrink_below_a_reserved_batch(self):
        self.client.post("/api/pedidos/", self.payload())
        self.assertEqual(
            self.client.patch(
                f"/api/plantas/{self.plants[0].pk}/", {"capacidade_l": 25}
            ).status_code,
            400,
        )

    def test_reset_is_applied_on_recipe_change_only(self):
        first = self.client.post("/api/pedidos/", self.payload()).data
        order = Pedido.objects.get(pk=first["idpedido"])
        end = order.lotes.latest("fim_previsto").fim_previsto
        for plant in self.plants:
            advance_batches(plant.pk, end)
        repeat = self.client.post("/api/pedidos/prever/", self.payload()).data
        self.assertEqual(repeat["setup_total_seg"], 0)
        self.client.patch(f"/api/receitas/{self.recipe['idreceita']}/", {"tempo1": 35})
        changed = self.client.post("/api/pedidos/prever/", self.payload()).data
        self.assertEqual(changed["setup_total_seg"], 80)

    def test_open_downtime_pauses_and_shifts_forecast_on_resume(self):
        order_id = self.client.post("/api/pedidos/", self.payload()).data["idpedido"]
        order = Pedido.objects.get(pk=order_id)
        batch = order.lotes.filter(planta=self.plants[0]).get()
        start = batch.inicio_previsto
        stop = Parada.objects.create(
            planta=self.plants[0], inicio=start + timedelta(seconds=1)
        )
        advance_batches(self.plants[0].pk, start + timedelta(seconds=2))
        batch.refresh_from_db()
        self.assertNotEqual(batch.status, "concluido")
        stop.fim = start + timedelta(seconds=22)
        stop.save()
        previous_end = batch.fim_previsto
        advance_batches(self.plants[0].pk, start + timedelta(seconds=22))
        batch.refresh_from_db()
        self.assertEqual(batch.fim_previsto, previous_end + timedelta(seconds=20))

    @override_settings(SIMULACAO_PRODUCAO=False)
    def test_disabled_simulation_does_not_actuate_or_complete(self):
        response = self.client.post("/api/pedidos/", self.payload())
        self.assertEqual(response.status_code, 201, response.data)
        order = Pedido.objects.get(pk=response.data["idpedido"])
        advance_batches(self.plants[0].pk, timezone.now() + timedelta(days=2))
        order.refresh_from_db()
        self.assertEqual(order.status, "pendente")
        self.assertFalse(order.lotes.exclude(status="planejado").exists())
