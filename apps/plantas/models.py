from django.db import models
from apps.accounts.models import Empresa
import uuid


class Planta(models.Model):
    idplanta = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    localizacao = models.CharField(max_length=45)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="plantas",
        db_column="empresa_idempresa",
    )

    suspensa_desde = models.DateTimeField(null=True, blank=True)
    capacidade_l = models.FloatField(default=50)
    tempo_reset_seg = models.FloatField(default=60)
    ultima_receita = models.ForeignKey(
        "producao.Receita",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    ultima_receita_versao = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = "planta"

    def clp_controle(self, clps=None):
        """CLP que executa os ciclos desta planta (tem um tanque da planilha)."""
        clps = self.clps.all() if clps is None else clps
        return min(
            (c for c in clps if c.ativo and c.tanque),
            key=lambda c: c.pk,
            default=None,
        )

    def __str__(self):
        return f"{self.nome} {self.empresa.nome}"


class Clp(models.Model):
    idclp = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    ip = models.GenericIPAddressField(protocol="both")
    porta = models.CharField(max_length=45)
    status = models.CharField(max_length=45)
    ativo = models.BooleanField()
    escrita_habilitada = models.BooleanField(default=False)
    ultima_comunicacao = models.DateTimeField(null=True, blank=True)
    # Tanque da planilha (TK1/TK2) que esta planta usa para produzir. Vazio: o
    # CLP é só monitorado e a planta segue na execução simulada.
    tanque = models.CharField(
        max_length=3, blank=True, default="",
        choices=[("TK1", "TK1"), ("TK2", "TK2")],
    )
    # Última leitura do bloco do tanque: etapa, níveis, tempos, status e modo.
    estado_tanque = models.JSONField(default=dict, blank=True)
    planta = models.ForeignKey(
        Planta,
        on_delete=models.CASCADE,
        related_name="clps",
        db_column="planta_idplanta",
    )

    class Meta:
        db_table = "clp"

    @property
    def modo(self):
        return self.estado_tanque.get("modo")

    @property
    def mes_liberado(self):
        """Só o MODO 2 entrega o tanque ao MES; 0 (local) e 1 (aparelho) bloqueiam."""
        from services.modbus_map import MODO_MES

        return bool(self.tanque) and self.modo == MODO_MES

    def __str__(self):
        return f"{self.nome} ({self.ip}:{self.porta})"


class Sensor(models.Model):

    class Tipo(models.TextChoices):
        VOLUME = "volume", "Volume"
        TEMPERATURA = "temperatura", "Temperatura"
        PRESSAO = "pressao", "Pressão"
        VAZAO = "vazao", "Vazão"
        PROCESSO = "processo", "Variável de processo"
        NIVEL = "nivel", "Nível"
        TEMPO = "tempo", "Tempo"

    class TipoRegistro(models.TextChoices):
        COIL = "coil", "Coil"
        HOLDING_REGISTER = "holding_register", "Holding Register"
        INPUT_STATUS = "input_status", "Input Status"

    UNIDADES_POR_TIPO = {
        Tipo.VOLUME: {"litros": "L", "ml": "mL", "m3": "m³"},
        Tipo.TEMPERATURA: {"celsius": "°C", "fahrenheit": "°F", "kelvin": "K"},
        Tipo.PRESSAO: {"bar": "bar", "pascal": "Pa", "kpa": "kPa", "psi": "psi"},
        Tipo.VAZAO: {"l_min": "L/min", "l_s": "L/s", "m3_h": "m³/h"},
        Tipo.NIVEL: {"litros": "L", "percentual": "%", "cm": "cm", "mm": "mm", "bruto": "bruto"},
        Tipo.TEMPO: {"segundos": "s", "minutos": "min", "ms": "ms", "bruto": "bruto"},
        Tipo.PROCESSO: {"bruto": "bruto", "bit": "bit", "sem_unid": "sem unidade"},
    }

    idsensor = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    unidade = models.CharField(max_length=10)
    minimo = models.FloatField()
    maximo = models.FloatField()
    tipo_registro = models.CharField(max_length=20, choices=TipoRegistro.choices)
    endereco = models.PositiveIntegerField()
    gravavel = models.BooleanField(default=False)
    clp = models.ForeignKey(Clp, on_delete=models.CASCADE, related_name="sensores")

    class Meta:
        db_table = "sensor"

    @property
    def unidade_exibicao(self):
        return self.UNIDADES_POR_TIPO.get(self.tipo, {}).get(self.unidade, self.unidade)

    @property
    def pode_escrever(self):
        return (
            self.clp.ativo
            and self.clp.escrita_habilitada
            and self.gravavel
            and self.tipo_registro in (self.TipoRegistro.COIL, self.TipoRegistro.HOLDING_REGISTER)
        )

    def __str__(self):
        return f"{self.nome} ({self.tipo})"


class Leitura(models.Model):
    idleitura = models.AutoField(primary_key=True)
    valor = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sensor = models.ForeignKey(
        Sensor, on_delete=models.CASCADE, related_name="leituras"
    )

    class Meta:
        indexes = [
            models.Index(fields=["sensor", "-timestamp"]),
            models.Index(fields=["timestamp"]),
        ]
        db_table = "leitura"
        ordering = ["-timestamp"]
