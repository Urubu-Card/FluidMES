from django.db import models
from apps.accounts.models import Empresa


class Planta(models.Model):
    idplanta    = models.AutoField(primary_key=True)
    nome        = models.CharField(max_length=45)
    localizacao = models.CharField(max_length=45)
    empresa     = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='plantas',
        db_column='empresa_idempresa',
    )

    class Meta:
        db_table = 'planta'
        verbose_name = 'Planta'
        verbose_name_plural = 'Plantas'

    def __str__(self):
        return self.nome


class Clp(models.Model):
    idclp  = models.AutoField(primary_key=True)
    nome   = models.CharField(max_length=45)
    ip     = models.GenericIPAddressField(protocol='both')
    porta  = models.CharField(max_length=45)
    status = models.CharField(max_length=45)
    planta = models.ForeignKey(
        Planta,
        on_delete=models.CASCADE,
        related_name='clps',
        db_column='planta_idplanta',
    )

    class Meta:
        db_table = 'clp'
        verbose_name = 'CLP'
        verbose_name_plural = 'CLPs'

    def __str__(self):
        return f'{self.nome} ({self.ip}:{self.porta})'
