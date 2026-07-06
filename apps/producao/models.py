from django.db import models
from apps.accounts.models import Empresa, Usuarios


class Receita(models.Model):
    idreceita    = models.AutoField(primary_key=True)
    nome         = models.CharField(max_length=45)
    ingrediente1 = models.FloatField()
    ingrediente2 = models.FloatField()
    ingrediente3 = models.FloatField()
    tempo1       = models.FloatField()
    tempo2       = models.FloatField()

    class Meta:
        db_table = 'receita'
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    class Status(models.TextChoices):
        PENDENTE     = 'pendente',     'Pendente'
        EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
        CONCLUIDO    = 'concluido',    'Concluído'
        CANCELADO    = 'cancelado',    'Cancelado'

    class Aprovacao(models.TextChoices):
        AGUARDANDO = 'aguardando', 'Aguardando'
        APROVADO   = 'aprovado',   'Aprovado'
        REPROVADO  = 'reprovado',  'Reprovado'

    idpedido   = models.AutoField(primary_key=True)
    prazo      = models.DateField()
    quantidade = models.FloatField()
    pedidocol  = models.CharField(max_length=45, blank=True, null=True)
    status     = models.CharField(max_length=20, choices=Status.choices,   default=Status.PENDENTE)
    aprovacao  = models.CharField(max_length=20, choices=Aprovacao.choices, default=Aprovacao.AGUARDANDO)
    receita    = models.ForeignKey(Receita,  on_delete=models.PROTECT, related_name='pedidos', db_column='receita_idreceita')
    usuario    = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True, related_name='pedidos', db_column='usuarios_idusuario')
    empresa    = models.ForeignKey(Empresa,  on_delete=models.CASCADE, related_name='pedidos', db_column='empresa_idempresa')

    class Meta:
        db_table = 'pedido'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.idpedido} - {self.receita.nome}'
