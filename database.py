--------------------------------------------------------------------------------------------------------------------------------

#Imports

#Importa o sistema ORM do Django (tipo um tradutor para SQL e Django)
from django.db import models

#AbstractUser para autenticação do Django
#BaseUserManager para gerenciar a criação dos usuários
from django.contrib.auth.models import AbstractUser, BaseUserManager

#Para acessar configurações do projeto
from django.conf import settings

#Validação dos valores
from django.core.validators import MinValueValidator, MaxValueValidator

--------------------------------------------------------------------------------------------------------------------------------

#Criacao para os adm
class UsuariosManager(BaseUserManager):
    #Funcao para criacao de um usuário comum
    def create_user(self, email, password=None, **extra_fields):
        #Padroniza email, tipo, de um TESTE@GMAIL.COM, vai para teste@gmail.com
        email = self.normalize_email(email)
        #Cria objeto do usuário
        user = self.model(email=email, **extra_fields)
        #Criptografia da senha
        user.set_password(password)
        #Salvamento no banco
        user.save(using=self._db)
        return user
    
    #Funcao para criacao do admin
    def create_superuser(self, email, password=None, **extra_fields):
        #Permissão de staff/admin
        extra_fields.setdefault("is_staff", True)
        #Permissão total
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

--------------------------------------------------------------------------------------------------------------------------------

#Criacao da tabela empresa
class Empresa(models.Model):
    #Id
    idempresa = models.AutoField(primary_key=True)
    #Nome da empresa
    nome = models.CharField(max_length=256)
    #CNPJ
    cnpj = models.CharField(max_length=18, unique=True)

    #Configurações da tabela
    class Meta:
        #Nome da tabela no SQL
        db_table = "empresa"
        # Nome da empresa
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
    #Forma de texto
    def __str__(self):
        return self.nome

--------------------------------------------------------------------------------------------------------------------------------

#Criacao tabela usuarios
class Usuarios(AbstractUser):
    #Enum para os tipos de cargos
    class Role(models.IntegerChoices):
        PREPOSTO = 1, "Preposto"
        OPERADOR = 2, "Chefe"
        VISUALIZADOR = 3, "Funcionario"

    #Remocao dos campos padroes do django
    #Remove o username padrao
    username = None
    #Remove o first_name e o last_name
    first_name = None
    last_name = None
    #Gerenciamento customizado
    objects = UsuariosManager()

    #Campos da tabela
    #Id
    idusuario = models.AutoField(primary_key=True)
    # Email/login
    email = models.EmailField(max_length=256, unique=True)
    #Nome completo
    nome = models.CharField(max_length=256)
    #CPF
    cpf = models.CharField(max_length=14, unique=True)
    #Perfil do usuário
    role = models.IntegerField(choices=Role.choices, default=Role.VISUALIZADOR)

    #Relacionamento usuarios com a empresa (cada usuario para uma empresa)
    empresa = models.ForeignKey(
        #Tabela que tem relacao
        Empresa,
        #Se empresa for deletada os usuarios dela tambem serão deletados
        on_delete=models.CASCADE,
        #Permite empresa.usuarios.all()
        related_name="usuarios",
        #Nome da coluna no SQL
        db_column="empresa_idempresa",
        #Campo obrigatório
        null=False,
        #Pode ficar vazio no formulário
        blank=True,
        #Empresa que e padrao
        default=1
    )

    #Configuracao do login

    #Campo usado como login
    USERNAME_FIELD = "email"
    #Campos obrigatórios ao criar um adm
    REQUIRED_FIELDS = ["nome", "cpf"]

    #Configurcoes da tabela
    class Meta:
        #Nome da tabela no SQL
        db_table = "usuarios"
        #Nome do usario
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
    #Representacao em texto
    def __str__(self):
        return self.nome

--------------------------------------------------------------------------------------------------------------------------------

#Tabela planta
class Planta(models.Model):
    #Id 
    idplanta = models.AutoField(primary_key=True)
    #Nome da planta
    nome = models.CharField(max_length=45)
    #Localização da planta
    localizacao = models.CharField(max_length=45)

    #Relacionamento da planta com a empresa
    empresa = models.ForeignKey(
        #Tabela que tem relacao
        Empresa,
        #Se empresa for deletada as plantas dela tambem serao
        on_delete=models.CASCADE,
        #Permite o empresa.plantas.all()
        related_name="plantas",
        db_column="empresa_idempresa",
    )

    #Configuracoes da tabela
    class Meta:
        #Nome da tabela no SQL
        db_table = "planta"
        #Nome da Planta
        verbose_name = "Planta"
        verbose_name_plural = "Plantas"
    #Representacao em texto
    def __str__(self):
        return self.nome

--------------------------------------------------------------------------------------------------------------------------------

#Tabela CLP
class Clp(models.Model):
    #Id
    idclp = models.AutoField(primary_key=True)
    #Nome do CLP
    nome = models.CharField(max_length=45)
    #Endereço IP 
    ip = models.GenericIPAddressField(
    #Aceita tanto IPv4 quanto IPv6
        protocol="both"
    )
    #Porta de comunicação
    porta = models.CharField(max_length=45)
    #Status do CLP
    status = models.CharField(max_length=45)

    # -----------------------------------------------------
    # RELACIONAMENTO COM PLANTA
    # -----------------------------------------------------

    planta = models.ForeignKey(

        Planta,

        # Se planta for deletada,
        # CLPs também serão
        on_delete=models.CASCADE,

        # Permite:
        # planta.clps.all()
        related_name="clps",

        db_column="planta_idplanta",
    )

    class Meta:

        db_table = "clp"

        verbose_name = "CLP"
        verbose_name_plural = "CLPs"

    def __str__(self):

        # Exemplo:
        # CLP01 (192.168.0.10:502)
        return f"{self.nome} ({self.ip}:{self.porta})"


# =========================================================
# TABELA RECEITA
# =========================================================

class Receita(models.Model):

    # Chave primária
    idreceita = models.AutoField(
        primary_key=True
    )

    # Nome da receita
    nome = models.CharField(
        max_length=45
    )

    # Ingredientes
    ingrediente1 = models.FloatField()
    ingrediente2 = models.FloatField()
    ingrediente3 = models.FloatField()

    # Tempos do processo
    tempo1 = models.FloatField()
    tempo2 = models.FloatField()

    class Meta:

        db_table = "receita"

        verbose_name = "Receita"
        verbose_name_plural = "Receitas"

    def __str__(self):
        return self.nome


# =========================================================
# TABELA PEDIDO
# =========================================================

class Pedido(models.Model):

    # -----------------------------------------------------
    # ENUM DE STATUS
    # -----------------------------------------------------

    class Status(models.TextChoices):

        PENDENTE = "pendente", "Pendente"

        EM_ANDAMENTO = (
            "em_andamento",
            "Em Andamento"
        )

        CONCLUIDO = "concluido", "Concluído"

        CANCELADO = "cancelado", "Cancelado"

    # -----------------------------------------------------
    # ENUM DE APROVAÇÃO
    # -----------------------------------------------------

    class Aprovacao(models.TextChoices):

        AGUARDANDO = "aguardando", "Aguardando"

        APROVADO = "aprovado", "Aprovado"

        REPROVADO = "reprovado", "Reprovado"

    # -----------------------------------------------------
    # CAMPOS DA TABELA
    # -----------------------------------------------------

    # Chave primária
    idpedido = models.AutoField(
        primary_key=True
    )

    # Prazo do pedido
    prazo = models.DateField()

    #Relacionamento com a receita
    receita = models.ForeignKey(
        Receita,
        #Impede deletar uma receita se existir.algum pedido usando ela
        on_delete=models.PROTECT,
        # Permite receita.pedidos.all()
        related_name="pedidos",
        db_column="receita_idreceita",
    )

    #Quantidade da produção
    quantidade = models.FloatField()
    #Campo que é opcional
    pedidocol = models.CharField(
        max_length=45,
        blank=True,
        null=True
    )

    #Relacionamento com o usuario
    usuario = models.ForeignKey(
        Usuarios,
        #Se usuário for deletado, campo vira NULL (deixa o valor desconhecido)
        on_delete=models.SET_NULL,
        null=True,
        related_name="pedidos",
        db_column="usuarios_idusuario",
    )

    #Status do pedido
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )

    #Processo de aprovação do pedido
    aprovacao = models.CharField(
        max_length=20,
        choices=Aprovacao.choices,
        default=Aprovacao.AGUARDANDO,
    )

    #Relacionamento com a empresa
    empresa = models.ForeignKey(
        Empresa,
        #Se empresa for deletada os pedidos dela também serão deletados
        on_delete=models.CASCADE,
        related_name="pedidos",
        db_column="empresa_idempresa",
    )

    #Configurações da tabela
    class Meta:
        db_table = "pedido"
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    #Forma de texto
    def __str__(self):
        #Exemplo:
        #Pedido #10 - Receita A
        return f"Pedido #{self.idpedido} - {self.receita.nome}"