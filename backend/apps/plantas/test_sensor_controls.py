from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone
from rest_framework.test import APITestCase

from apps.accounts.models import Atualizacao, Empresa, Usuarios
from services.clp_control import EscritaRecusada
from .models import Clp, Leitura, Planta, Sensor


class SensorControlsTests(APITestCase):
    def setUp(self):
        empresa = Empresa.objects.create(nome="Fábrica", cnpj="teste-a")
        self.preposto = Usuarios.objects.create_user(
            email="preposto@teste.example", empresa=empresa, cpf="teste-a", role=1
        )
        planta = Planta.objects.create(nome="Linha", localizacao="Setor", empresa=empresa)
        self.clp = Clp.objects.create(
            nome="CLP", ip="127.0.0.1", porta="5020", ativo=True,
            escrita_habilitada=True, planta=planta,
        )
        self.sensor = Sensor.objects.create(
            nome="Pressão", tipo="pressao", unidade="bar", minimo=1,
            maximo=100, tipo_registro="holding_register", endereco=6,
            clp=self.clp, gravavel=True,
        )
        self.url = f"/api/sensores/{self.sensor.pk}/"
        self.client.force_authenticate(self.preposto)

    def test_units_are_validated_by_type_and_legacy_values_are_preserved(self):
        unidades = self.client.get("/api/sensores/unidades/").data
        self.assertEqual(unidades["temperatura"]["celsius"], "°C")
        self.assertEqual(self.client.patch(self.url, {"unidade": "litros"}).status_code, 400)
        self.assertEqual(self.client.patch(self.url, {"tipo": "temperatura"}).status_code, 400)
        response = self.client.patch(self.url, {"tipo": "temperatura", "unidade": "celsius"})
        self.assertEqual(response.data["unidade_label"], "°C")
        self.sensor.unidade = "custom"
        self.sensor.save(update_fields=["unidade"])
        self.assertEqual(self.client.patch(self.url, {"nome": "Renomeado"}).status_code, 200)

    def test_status_uses_latest_reading_and_limits(self):
        self.assertEqual(self.client.get(self.url).data["estado"], "sem_leitura")
        leitura = Leitura.objects.create(sensor=self.sensor, valor=101)
        sensor = self.client.get(self.url).data
        self.assertEqual(sensor["estado"], "fora_limite")
        self.assertEqual(sensor["valor_atual"], 101)
        Leitura.objects.filter(pk=leitura.pk).update(
            timestamp=timezone.now() - timedelta(seconds=20)
        )
        self.assertEqual(self.client.get(self.url).data["estado"], "desatualizado")

    @patch("apps.plantas.views.consultar", autospec=True)
    def test_write_validates_permissions_and_limits_then_audits_and_reads(self, consultar):
        url = self.url + "escrever/"
        for invalido in (-1, 101, 65536, True, 1.5):
            self.assertEqual(self.client.post(url, {"valor": invalido}, format="json").status_code, 400)
        self.clp.escrita_habilitada = False
        self.clp.save(update_fields=["escrita_habilitada"])
        self.assertEqual(self.client.post(url, {"valor": 20}, format="json").status_code, 403)
        self.clp.escrita_habilitada = True
        self.clp.save(update_fields=["escrita_habilitada"])
        self.sensor.gravavel = False
        self.sensor.save(update_fields=["gravavel"])
        self.assertEqual(self.client.post(url, {"valor": 20}, format="json").status_code, 403)
        self.sensor.gravavel = True
        self.sensor.save(update_fields=["gravavel"])
        consultar.assert_not_called()

        consultar.return_value = 20
        result = self.client.post(url, {"valor": 20}, format="json")
        self.assertEqual(result.status_code, 200, result.data)
        consultar.assert_awaited_once_with(self.sensor, comando=20)
        self.assertEqual(self.client.get(self.url).data["valor_atual"], 20)
        self.assertTrue(Atualizacao.objects.filter(recurso="Modbus", autor=self.preposto).exists())

    @patch("apps.plantas.views.consultar", autospec=True)
    def test_coil_confirmation_and_rejection_are_distinct_from_readback(self, consultar):
        self.sensor.tipo_registro = "coil"
        self.sensor.save(update_fields=["tipo_registro"])
        url = self.url + "escrever/"
        self.assertEqual(self.client.post(url, {"valor": 1}, format="json").status_code, 400)
        consultar.return_value = 0
        self.assertEqual(self.client.post(url, {"valor": True}, format="json").data["valor"], 0)
        consultar.return_value = None
        self.assertEqual(self.client.post(url, {"valor": False}, format="json").data["valor"], None)
        consultar.side_effect = EscritaRecusada("ocupado")
        self.assertEqual(self.client.post(url, {"valor": True}, format="json").status_code, 422)
        self.assertEqual(Leitura.objects.count(), 1)

    @patch("apps.plantas.views.consultar", autospec=True)
    def test_discrete_inputs_and_other_companies_cannot_write(self, consultar):
        self.sensor.tipo_registro = "input_status"
        self.sensor.save(update_fields=["tipo_registro"])
        url = self.url + "escrever/"
        self.assertEqual(self.client.post(url, {"valor": True}, format="json").status_code, 403)
        outra_empresa = Empresa.objects.create(nome="Outra", cnpj="teste-b")
        outro_preposto = Usuarios.objects.create_user(
            email="outro@teste.example", empresa=outra_empresa, cpf="teste-b", role=1
        )
        self.client.force_authenticate(outro_preposto)
        self.assertEqual(self.client.post(url, {"valor": 20}, format="json").status_code, 404)
        consultar.assert_not_called()
