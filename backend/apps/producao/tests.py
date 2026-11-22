from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from apps.accounts.models import Empresa
from apps.plantas.models import Planta
from .models import Receita, Pedido, Parada, OEERegistro
from .tasks import _calcular_oee_planta


class OeeTests(TestCase):
    def test_midnight_overlaps_actual_completion_and_idempotency(self):
        company = Empresa.objects.create(nome="A", cnpj="test")
        plant = Planta.objects.create(nome="P", localizacao="A", empresa=company)
        recipe = Receita.objects.create(
            nome="R",
            empresa=company,
            ingrediente1=1,
            ingrediente2=0,
            ingrediente3=0,
            tempo1=30,
            tempo2=30,
        )
        start = timezone.make_aware(datetime(2026, 10, 18))
        Parada.objects.create(
            planta=plant,
            inicio=start - timedelta(hours=1),
            fim=start + timedelta(hours=1),
        )
        Parada.objects.create(
            planta=plant,
            inicio=start + timedelta(minutes=30),
            fim=start + timedelta(hours=2),
        )
        Pedido.objects.create(
            planta=plant,
            empresa=company,
            receita=recipe,
            prazo="2027-01-01",
            status="concluido",
            aprovacao="aprovado",
            quantidade=180,
            quantidade_boa=162,
            concluido_em=start + timedelta(hours=4),
        )
        result = _calcular_oee_planta(plant, start.date())
        self.assertEqual(result.tempo_parado_min, 120)
        self.assertEqual(result.quantidade_produzida, 180)
        self.assertAlmostEqual(result.oee, 0.75 * 0.5 * 0.9)
        _calcular_oee_planta(plant, start.date())
        self.assertEqual(OEERegistro.objects.count(), 1)

    def test_empty_oee_has_no_division_by_zero(self):
        record = OEERegistro(
            tempo_planejado_min=0,
            tempo_parado_min=0,
            quantidade_produzida=0,
            quantidade_boa=0,
            tempo_ciclo_ideal_seg=0,
        )
        self.assertEqual(record.oee, 0)


from django.test import override_settings
from rest_framework.test import APIClient
from apps.accounts.models import Usuarios, Atualizacao
from apps.producao.models import Solicitacao
from .workflow import advance_plant


class WorkflowTests(TestCase):
    def setUp(self):
        self.company = Empresa.objects.create(nome="Flow", cnpj="flow")
        self.other_company = Empresa.objects.create(nome="Other", cnpj="other")
        self.owner = Usuarios.objects.create_user(
            email="owner@flow.test",
            password="Flow-password-123!",
            cpf="owner",
            empresa=self.company,
            role=1,
        )
        self.chief = Usuarios.objects.create_user(
            email="chief@flow.test",
            password="Flow-password-123!",
            cpf="chief",
            empresa=self.company,
            role=2,
        )
        self.employee = Usuarios.objects.create_user(
            email="worker@flow.test",
            password="Flow-password-123!",
            cpf="worker",
            empresa=self.company,
            role=3,
        )
        self.other = Usuarios.objects.create_user(
            email="other@flow.test",
            password="Flow-password-123!",
            cpf="other",
            empresa=self.other_company,
            role=1,
        )
        self.plant = Planta.objects.create(
            nome="P", localizacao="A", empresa=self.company
        )
        self.recipe = Receita.objects.create(
            nome="R",
            empresa=self.company,
            ingrediente1=1,
            ingrediente2=2,
            ingrediente3=0,
            tempo1=1,
            tempo2=1,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.employee)

    def order(self):
        return self.client.post(
            "/api/pedidos/",
            {
                "planta": self.plant.pk,
                "receita": self.recipe.pk,
                "quantidade": 10,
                "prazo": "2027-01-01",
            },
        )

    def test_plant_is_only_created_once_after_approval(self):
        response = self.client.post(
            "/api/plantas/", {"nome": "Requested", "localizacao": "B"}
        )
        self.assertEqual(response.status_code, 202, response.data)
        self.assertFalse(Planta.objects.filter(nome="Requested").exists())
        url = f"/api/solicitacoes/{response.data['solicitacao_id']}/aprovar/"
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_authenticate(self.chief)
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 400)
        self.assertEqual(Planta.objects.filter(nome="Requested").count(), 1)

    def test_recipe_request_rejection_does_not_create_recipe(self):
        payload = {
            "nome": "Request",
            "ingrediente1": 1,
            "ingrediente2": 2,
            "ingrediente3": 3,
            "tempo1": 1,
            "tempo2": 2,
        }
        response = self.client.post("/api/receitas/", payload)
        self.assertEqual(response.status_code, 202)
        self.client.force_authenticate(self.owner)
        self.assertEqual(
            self.client.post(
                f"/api/solicitacoes/{response.data['solicitacao_id']}/recusar/"
            ).status_code,
            200,
        )
        self.assertFalse(Receita.objects.filter(nome="Request").exists())

    def test_request_data_is_validated_before_queueing(self):
        self.assertEqual(
            self.client.post("/api/plantas/", {"nome": "X"}).status_code, 400
        )
        self.assertEqual(Solicitacao.objects.count(), 0)

    def test_tenant_isolation_for_approvals(self):
        response = self.client.post("/api/plantas/", {"nome": "X", "localizacao": "Y"})
        self.client.force_authenticate(self.other)
        self.assertEqual(len(self.client.get("/api/solicitacoes/").data), 0)
        self.assertEqual(
            self.client.post(
                f"/api/solicitacoes/{response.data['solicitacao_id']}/aprovar/"
            ).status_code,
            404,
        )

    def test_employee_sees_only_own_orders_and_requests(self):
        mine = self.order().data
        self.client.force_authenticate(self.chief)
        self.order()
        self.client.force_authenticate(self.employee)
        orders = self.client.get("/api/pedidos/").data
        self.assertEqual([o["idpedido"] for o in orders], [mine["idpedido"]])

    def test_chief_order_auto_approval_and_single_plant_queue(self):
        self.client.force_authenticate(self.chief)
        first = self.order().data
        second = self.order().data
        self.assertEqual(first["status"], "em_andamento")
        self.assertEqual(first["aprovacao"], "aprovado")
        self.assertEqual(second["status"], "pendente")
        self.assertEqual(second["aprovacao"], "aprovado")
        order = Pedido.objects.get(pk=first["idpedido"])
        advance_plant(
            self.plant.pk,
            order.lotes.latest("fim_previsto").fim_previsto - timedelta(seconds=1),
        )
        order.refresh_from_db()
        self.assertEqual(order.status, "em_andamento")
        at = order.lotes.latest("fim_previsto").fim_previsto
        advance_plant(self.plant.pk, at)
        order.refresh_from_db()
        self.assertEqual(order.status, "concluido")
        next_order = Pedido.objects.get(pk=second["idpedido"])
        self.assertEqual(next_order.status, "em_andamento")
        self.assertEqual(next_order.iniciado_em, at)
        self.assertEqual(Pedido.objects.filter(status="em_andamento").count(), 1)
        self.assertEqual(OEERegistro.objects.count(), 1)

    def test_worker_restart_can_finish_due_order(self):
        from django.core.management import call_command

        self.client.force_authenticate(self.chief)
        first = self.order().data
        from .models import LoteProducao

        past = timezone.now() - timedelta(seconds=30)
        LoteProducao.objects.filter(pedido_id=first["idpedido"]).update(
            inicio_previsto=past,
            iniciado_em=past,
            fim_previsto=past + timedelta(seconds=2),
        )
        call_command("run_production", once=True)
        self.assertEqual(Pedido.objects.get(pk=first["idpedido"]).status, "concluido")

    @override_settings(SIMULACAO_PRODUCAO=False)
    def test_real_mode_never_auto_completes_or_starts(self):
        self.client.force_authenticate(self.chief)
        response = self.order().data
        self.assertEqual(response["status"], "pendente")
        self.assertIsNone(response["iniciado_em"])

    def test_audit_excludes_own_actions_and_preserves_actor(self):
        self.client.post(
            "/api/plantas/", {"nome": "Employee request", "localizacao": "Y"}
        )
        self.client.force_authenticate(self.owner)
        self.client.post("/api/plantas/", {"nome": "Owner created", "localizacao": "Y"})
        data = self.client.get("/api/atualizacoes/").data["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["autor_cargo"], "Funcionário")
        self.assertEqual(data[0]["acao"], "solicitou")
        self.client.force_authenticate(self.chief)
        self.assertEqual(self.client.get("/api/atualizacoes/").status_code, 403)

    def test_preferences_are_per_user(self):
        self.assertEqual(self.client.get("/api/preferencias/").data["tema"], "sistema")
        self.assertEqual(
            self.client.patch("/api/preferencias/", {"tema": "claro"}).status_code, 200
        )
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.get("/api/preferencias/").data["tema"], "sistema")
        self.assertEqual(
            self.client.patch("/api/preferencias/", {"tema": "invalid"}).status_code,
            400,
        )

    def test_plant_card_exposes_actual_status_and_oee(self):
        self.client.force_authenticate(self.chief)
        self.order()
        card = self.client.get("/api/plantas/").data[0]["painel"]
        self.assertEqual(card["status"], "produzindo")
        self.assertEqual(card["receita"], "R")
        self.assertIsNone(card["oee"])

    def test_owner_can_edit_only_unapproved_orders(self):
        response = self.order().data
        url = f"/api/pedidos/{response['idpedido']}/"
        self.client.force_authenticate(self.chief)
        self.assertEqual(self.client.patch(url, {"quantidade": 12}).status_code, 403)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.patch(url, {"quantidade": 12}).status_code, 200)
        self.assertEqual(self.client.post(url + "aprovar/").status_code, 200)
        self.assertEqual(self.client.patch(url, {"quantidade": 15}).status_code, 400)
