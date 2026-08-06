from django.db import models
from apps.accounts.models import Empresa
import uuid

class Planta(models.Model):
    idplanta    = models.AutoField(primary_key=True)
    nome        = models.CharField(max_length=45)
    uuid        = models.UUIDField(default=uuid.uuid4,editable=False,unique=True)
    localizacao = models.CharField(max_length=45)
    empresa     = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='plantas',
        db_column='empresa_idempresa',
    )

    class Meta:
        db_table = 'planta'

    def __str__(self):
        return f"{self.nome} {self.empresa.nome}"


class Clp(models.Model):
    idclp  = models.AutoField(primary_key=True)
    nome   = models.CharField(max_length=45)
    ip     = models.GenericIPAddressField(protocol='both')
    porta  = models.CharField(max_length=45)
    status = models.CharField(max_length=45)
    ativo  = models.BooleanField()
    planta = models.ForeignKey(
        Planta,
        on_delete=models.CASCADE,
        related_name='clps',
        db_column='planta_idplanta',
    )

    class Meta:
        db_table = 'clp'

    def __str__(self):
        return f'{self.nome} ({self.ip}:{self.porta})'


class Sensor(models.Model):

    class Tipo(models.TextChoices):
        VOLUME      = 'volume',      'Volume'
        TEMPERATURA = 'temperatura', 'Temperatura'
        PRESSAO     = 'pressao',     'Pressão'

    class TipoRegistro(models.TextChoices):
        COIL             = 'coil',             'Coil'
        HOLDING_REGISTER = 'holding_register', 'Holding Register'
        INPUT_STATUS     = 'input_status',     'Input Status'

    idsensor      = models.AutoField(primary_key=True)
    nome          = models.CharField(max_length=45)
    tipo          = models.CharField(max_length=20, choices=Tipo.choices)
    unidade       = models.CharField(max_length=10)
    minimo        = models.FloatField()
    maximo        = models.FloatField()
    tipo_registro = models.CharField(max_length=20, choices=TipoRegistro.choices)
    endereco      = models.PositiveIntegerField()
    clp           = models.ForeignKey(Clp, on_delete=models.CASCADE, related_name='sensores')

    class Meta:
        db_table = 'sensor'

    def __str__(self):
        return f'{self.nome} ({self.tipo})'


class Leitura(models.Model):
    idleitura = models.AutoField(primary_key=True)
    valor     = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    sensor    = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='leituras')

    class Meta:
        db_table = 'leitura'
        ordering = ['-timestamp']