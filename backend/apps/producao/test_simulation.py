from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Atualizacao, Empresa, Usuarios
from apps.plantas.models import Planta
from .models import Pedido


@override_settings(SIMULACAO_PRODUCAO=True, SIMULACAO_SOB_DEMANDA=True)
class RequestDrivenSimulationTests(TestCase):
    def setUp(self):
        self.company = Empresa.objects.create(nome="Demo", cnpj="request-clock")
        self.owner = Usuarios.objects.create_user(
            email="clock@example.test",
            cpf="clock",
            password="StrongClock231!",
            empresa=self.company,
            role=1,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.owner)
        for i in range(2):
            Planta.objects.create(
                nome=f"T{i}",
                localizacao="A",
                empresa=self.company,
                capacidade_l=50,
                tempo_reset_seg=0,
            )
        recipe = self.client.post(
            "/api/receitas/",
            {
                "nome": "Demo",
                "tempo1": 5,
                "tempo2": 0,
                "componentes": [
                    {"nome": "A", "quantidade_l": 40, "vazao_l_min": 60},
                    {"nome": "B", "quantidade_l": 10, "vazao_l_min": 60},
                ],
            },
            format="json",
        )
        self.assertEqual(recipe.status_code, 201, recipe.data)
        result = self.client.post(
            "/api/pedidos/",
            {
                "receita": recipe.data["idreceita"],
                "quantidade": 200,
                "prazo": "2027-01-01",
            },
        )
        self.assertEqual(result.status_code, 201, result.data)
        self.order = Pedido.objects.get(pk=result.data["idpedido"])

    def test_reopening_reconciles_all_elapsed_cycles_once(self):
        end = self.order.lotes.latest("fim_previsto").fim_previsto
        with patch(
            "apps.producao.services.simulation.timezone.now",
            return_value=end + timedelta(seconds=1),
        ):
            response = self.client.post("/api/simulacao/sincronizar/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Cache-Control"], "no-store")
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, "concluido")
            self.assertEqual(self.order.quantidade_boa, 200)
            self.assertEqual(self.order.concluido_em, end)
            count = Atualizacao.objects.count()
            self.client.post("/api/simulacao/sincronizar/")
            self.assertEqual(Atualizacao.objects.count(), count)

    def test_clock_does_not_advance_another_company(self):
        other = Empresa.objects.create(nome="Other", cnpj="other-clock")
        self.owner.empresa = other
        self.owner.save()
        future = timezone.now() + timedelta(days=1)
        with patch(
            "apps.producao.services.simulation.timezone.now", return_value=future
        ):
            self.assertEqual(
                self.client.post("/api/simulacao/sincronizar/").status_code, 200
            )
        self.order.refresh_from_db()
        self.assertNotEqual(self.order.status, "concluido")

    @override_settings(SIMULACAO_PRODUCAO=False)
    def test_physical_mode_never_simulates_completion(self):
        future = timezone.now() + timedelta(days=1)
        with patch(
            "apps.producao.services.simulation.timezone.now", return_value=future
        ):
            response = self.client.post("/api/simulacao/sincronizar/")
        self.assertFalse(response.data["simulacao_sob_demanda"])
        self.order.refresh_from_db()
        self.assertNotEqual(self.order.status, "concluido")

    def test_clock_is_authenticated_and_post_only(self):
        self.assertEqual(
            self.client.get("/api/simulacao/sincronizar/").status_code, 405
        )
        self.client.force_authenticate(None)
        self.assertEqual(
            self.client.post("/api/simulacao/sincronizar/").status_code, 401
        )

    def test_pause_is_preserved_without_polling_between_open_and_close(self):
        batch = self.order.lotes.order_by("inicio_previsto", "pk").first()
        original_end = batch.fim_previsto
        paused_at = timezone.now() + timedelta(seconds=1)
        resumed_at = paused_at + timedelta(seconds=100)
        with patch(
            "apps.producao.services.simulation.timezone.now", return_value=paused_at
        ):
            response = self.client.post(
                "/api/paradas/",
                {
                    "planta": batch.planta_id,
                    "inicio": paused_at.isoformat(),
                    "fim": None,
                },
                format="json",
            )
        self.assertEqual(response.status_code, 201, response.data)
        with patch(
            "apps.producao.services.simulation.timezone.now", return_value=resumed_at
        ):
            closed = self.client.patch(
                f"/api/paradas/{response.data['idparada']}/",
                {"fim": resumed_at.isoformat()},
            )
        self.assertEqual(closed.status_code, 200, closed.data)
        batch.refresh_from_db()
        self.assertEqual(batch.fim_previsto, original_end + timedelta(seconds=100))
        self.assertNotEqual(batch.status, "concluido")
