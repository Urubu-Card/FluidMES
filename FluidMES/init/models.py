from django.db import models
from django.contrib.auth.models import AbstractUser ,BaseUserManager
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class UsuariosManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Empresa(models.Model):
    idempresa = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=256,)
    cnpj = models.CharField(max_length=18, unique=True)

    class Meta:
        db_table = "empresa"
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.nome


class Usuarios(AbstractUser):
    
    class Role(models.IntegerChoices):
        
        PREPOSTO     = 1, "Preposto"
        OPERADOR     = 2, "Chefe"
        VISUALIZADOR = 3, "Funcionario"

    username = None
    first_name =  None
    last_name = None

    objects = UsuariosManager()

    email = models.EmailField(max_length=256, unique=True)
    nome = models.CharField(max_length=256)
 
    cpf = models.CharField(max_length=14, unique=True)
    role = models.IntegerField(choices=Role.choices, default=Role.VISUALIZADOR)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="usuarios",
        db_column="empresa_idempresa",
        null=True,
        blank=True,
    )
 

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome", "cpf"]
 
    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
 
    def __str__(self):
        return self.nome
    

class Planta(models.Model):

    idplanta = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    localizacao = models.CharField(max_length=45)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="plantas",
        db_column="empresa_idempresa",
    )

    class Meta:
        db_table = "planta"
        verbose_name = "Planta"
        verbose_name_plural = "Plantas"

    def __str__(self):
        return self.nome


class Clp(models.Model):
    idclp = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    ip = models.GenericIPAddressField(protocol="both")
    porta = models.CharField(max_length=45)
    status = models.CharField(max_length=45)
    planta = models.ForeignKey(
        Planta,
        on_delete=models.CASCADE,
        related_name="clps",
        db_column="planta_idplanta",
    )

    class Meta:
        db_table = "clp"
        verbose_name = "CLP"
        verbose_name_plural = "CLPs"

    def __str__(self):
        return f"{self.nome} ({self.ip}:{self.porta})"


class Receita(models.Model):
    idreceita = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=45)
    ingrediente1 = models.FloatField()
    ingrediente2 = models.FloatField()
    ingrediente3 = models.FloatField()
    tempo1 = models.FloatField()
    tempo2 = models.FloatField()

    class Meta:
        db_table = "receita"
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EM_ANDAMENTO = "em_andamento", "Em Andamento"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    class Aprovacao(models.TextChoices):
        AGUARDANDO = "aguardando", "Aguardando"
        APROVADO = "aprovado", "Aprovado"
        REPROVADO = "reprovado", "Reprovado"

    idpedido = models.AutoField(primary_key=True)
    prazo = models.DateField()  # Considere usar models.DateField()
    receita = models.ForeignKey(
        Receita,
        on_delete=models.PROTECT,
        related_name="pedidos",
        db_column="receita_idreceita",
    )
    quantidade = models.FloatField()
    pedidocol = models.CharField(max_length=45, blank=True, null=True)
    usuario = models.ForeignKey(
        Usuarios,
        on_delete=models.SET_NULL,
        null=True,
        related_name="pedidos",
        db_column="usuarios_idusuario",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    aprovacao = models.CharField(
        max_length=20,
        choices=Aprovacao.choices,
        default=Aprovacao.AGUARDANDO,
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="pedidos",
        db_column="empresa_idempresa",
    )

    class Meta:
        db_table = "pedido"
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"Pedido #{self.idpedido} - {self.receita.nome}"