import uuid
from django.db                          import models
from django.conf                        import settings
from django.contrib.auth.models         import AbstractUser, BaseUserManager
from django.utils                       import timezone
from datetime                           import timedelta



class UsuariosManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', True)
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

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'cpf']#*Adicionar

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.first_name

