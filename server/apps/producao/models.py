from django.db            import models
from apps.accounts.models import Empresa, Usuarios
from apps.plantas.models  import Planta



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
    usuario    = models.ForeignKey(Usuarios, on_delete=models.SET_NULL,null=True, related_name='pedidos', db_column='usuarios_idusuario')
    empresa    = models.ForeignKey(Empresa,  on_delete=models.CASCADE, related_name='pedidos', db_column='empresa_idempresa')
    planta     = models.ForeignKey(Planta,   on_delete=models.CASCADE, related_name='pedidos', db_column='planta_idplanta')

    class Meta:
        db_table = 'pedido'
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.idpedido} - {self.receita.nome}'



class OEERegistro(models.Model):
    idoeeregistro = models.AutoField(primary_key=True)
    planta = models.ForeignKey(
        'plantas.Planta',
        on_delete=models.CASCADE,
        related_name='oee_registros',
        db_column='planta_idplanta',
    )
    data = models.DateField()

    # --- Disponibilidade ---
    tempo_planejado_min = models.IntegerField()          # ex: 480 (turno de 8h)
    tempo_parado_min    = models.IntegerField(default=0) # paradas no período

    # --- Performance ---
    quantidade_produzida  = models.FloatField(default=0)
    tempo_ciclo_ideal_seg = models.FloatField()  # snapshot do tempo de ciclo ideal (da Receita), em segundos/unidade

    # --- Qualidade ---
    quantidade_boa = models.FloatField(default=0)

    class Meta:
        db_table = 'oee_registro'
        unique_together = ('planta', 'data')
        ordering = ['-data']
        verbose_name = 'Registro de OEE'
        verbose_name_plural = 'Registros de OEE'

    def __str__(self):
        return f'{self.planta.nome} - {self.data}'

    @property
    def tempo_rodando_min(self):
        return max(self.tempo_planejado_min - self.tempo_parado_min, 0)

    @property
    def disponibilidade(self):
        if self.tempo_planejado_min == 0:
            return 0
        return self.tempo_rodando_min / self.tempo_planejado_min

    @property
    def performance(self):
        if self.tempo_rodando_min == 0 or self.tempo_ciclo_ideal_seg == 0:
            return 0
        tempo_rodando_seg = self.tempo_rodando_min * 60
        producao_teorica = tempo_rodando_seg / self.tempo_ciclo_ideal_seg
        if producao_teorica == 0:
            return 0
        return min(self.quantidade_produzida / producao_teorica, 1)

    @property
    def qualidade(self):
        if self.quantidade_produzida == 0:
            return 0
        return self.quantidade_boa / self.quantidade_produzida

    @property
    def oee(self):
        return self.disponibilidade * self.performance * self.qualidade
    
    
    
class Parada(models.Model):
    idparada  = models.AutoField(primary_key=True)
    planta    = models.ForeignKey(Planta,on_delete=models.CASCADE)
    inicio    = models.DateTimeField()
    fim       = models.DateTimeField(null=True)
    
    @property
    def duracao_min(self):
        if not self.fim:
            return 0
        return (self.fim - self.inicio).total_seconds() / 60
         
    class Meta:
        db_table = 'parada_planta'
        verbose_name = 'Parada da Planta'
        verbose_name_plural = 'Paradas das Plantas'