import uuid
from django.db                          import models
from django.conf                        import settings
from django.contrib.auth.models         import AbstractUser, BaseUserManager
from django.utils                       import timezone
from datetime                           import timedelta



class UsuariosManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('E-mail obrigatório.')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', self.model.Role.PREPOSTO)
        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError('Superusuário exige is_staff e is_superuser.')
        return self.create_user(email, password, **extra_fields)

class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE ,related_name='reset_tokens')
    token = models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    
    def is_valid(self):
        expira_em = self.criado_em +timedelta(hours=1)
        return not self.used and timezone.now() < expira_em
    


class Empresa(models.Model):
    idempresa = models.AutoField(primary_key=True)
    nome      = models.CharField(max_length=256)
    cnpj      = models.CharField(max_length=18, unique=True)

    class Meta:
        db_table = 'empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome


class Usuarios(AbstractUser):

    class Role(models.IntegerChoices):
        PREPOSTO     = 1, 'Preposto'
        OPERADOR     = 2, 'Chefe'
        VISUALIZADOR = 3, 'Funcionário'

    username   = None

    objects = UsuariosManager()
    email   = models.EmailField(max_length=256, unique=True)
    cpf     = models.CharField(max_length=14, unique=True)
    role    = models.IntegerField(choices=Role.choices, default=Role.VISUALIZADOR)
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='usuarios',
        db_column='empresa_idempresa',
        null=True,
        blank=True,
    )

    @property
    def is_preposto(self):
        return self.role == self.Role.PREPOSTO

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'cpf']#*Adicionar

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.first_name



class Preferencias(models.Model):
    usuario = models.OneToOneField(Usuarios, on_delete=models.CASCADE, related_name='preferencias')
    tema = models.CharField(max_length=10, default='sistema', choices=[('sistema','Dispositivo'),('escuro','Escuro'),('claro','Claro')])
    sidebar_desktop = models.CharField(max_length=10, default='aberta', choices=[('aberta','Aberta'),('icones','Ícones'),('hover','Expandir ao passar o mouse')])
    sidebar_mobile = models.CharField(max_length=10, default='puxador', choices=[('puxador','Puxador'),('icones','Ícones'),('hamburguer','Menu hambúrguer')])

class Atualizacao(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    autor = models.ForeignKey(Usuarios, null=True, on_delete=models.SET_NULL)
    autor_nome = models.CharField(max_length=310)
    autor_cargo = models.CharField(max_length=30)
    acao = models.CharField(max_length=40)
    recurso = models.CharField(max_length=60)
    descricao = models.CharField(max_length=500)
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta:
        ordering = ['-criado_em', '-pk']
