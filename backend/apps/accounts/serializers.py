from django.db import transaction
from validate_docbr                             import CPF, CNPJ
from rest_framework                             import serializers
from apps.accounts.models                       import Usuarios , Empresa
from django.contrib.auth                        import authenticate
from django.contrib.auth                        import get_user_model
from django.contrib.auth.password_validation    import validate_password

User = get_user_model()

validator_cpf = CPF()
validator_cnpj = CNPJ()

class PasswordRestRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    

class PasswordRestConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    nova_senha = serializers.CharField(write_only= True,validators= [validate_password])

class EmpresaSerializer(serializers.ModelSerializer):
     
     class Meta:
        model = Empresa
        fields = ['idempresa','nome','cnpj']
        
        

class UsuarioSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer(read_only=True)
    
    class Meta:
        model  = Usuarios
        fields = ['id', 'email', 'first_name','last_name', 'cpf', 'role', 'empresa']
        

class CadastroSerializer(serializers.Serializer):
    # Public signup always creates the company's Preposto. Client role is ignored.
    role = serializers.IntegerField(read_only=True)
    first_name          = serializers.CharField(max_length=150)
    last_name           = serializers.CharField(max_length=150)
    email               = serializers.EmailField()
    cpf                 = serializers.CharField(max_length=14)
    password            = serializers.CharField(write_only=True,validators = [validate_password])
    nomeEmpresa         = serializers.CharField(max_length=256)
    cnpj                = serializers.CharField(max_length=18)
    
    
    def validate_cpf(self, value):
        if not validator_cpf.validate(value):
            raise serializers.ValidationError("CPF Invalido")
        value = validator_cpf.mask(value)
        if Usuarios.objects.filter(cpf=value).exists():
            raise serializers.ValidationError('CPF já cadastrado.')
        return value

    def validate_email(self, value):
        value = value.lower()
        if Usuarios.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('E-mail já cadastrado.')
        return value

    def validate_cnpj(self, value):
        if not validator_cnpj.validate(value):
            raise serializers.ValidationError("CNPJ Invalido")
        value = validator_cnpj.mask(value)
        if Empresa.objects.filter(cnpj=value).exists():
            raise serializers.ValidationError('CNPJ já cadastrado.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        empresa = Empresa.objects.create(
            nome= validated_data['nomeEmpresa'],
            cnpj= validated_data['cnpj']
        )
        
        return Usuarios.objects.create_user(
            first_name = validated_data['first_name'],
            last_name  = validated_data['last_name'],
            email      = validated_data['email'],
            password   = validated_data['password'],
            cpf        = validated_data['cpf'],
            empresa    = empresa, role=Usuarios.Role.PREPOSTO)
        
        

class LoginSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        user = authenticate(
            self.context['request'],
            username =data['usuario'],
            password =data['password'],
        )
        
        if not user:
            raise serializers.ValidationError("CPF/E-mail ou senha incorretos")
        data['user'] = user
        return data
    
    
class FuncionarioSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer(read_only=True)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    class Meta:
        model = Usuarios
        fields = ['id', 'email', 'first_name', 'last_name', 'cpf', 'role', 'is_active', 'empresa', 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        value = value.lower()
        qs = Usuarios.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('E-mail já cadastrado.')
        return value

    def validate_cpf(self, value):
        if not validator_cpf.validate(value):
            raise serializers.ValidationError('CPF inválido.')
        value = validator_cpf.mask(value)
        qs = Usuarios.objects.filter(cpf=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('CPF já cadastrado.')
        return value

    def validate_role(self, value):
        if value not in (2, 3):
            raise serializers.ValidationError('Escolha Chefe ou Funcionário.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Informe uma senha inicial.'})
        return Usuarios.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


from .models import Preferencias, Atualizacao

class PreferenciasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preferencias
        fields = ['tema', 'sidebar_desktop', 'sidebar_mobile']

class AtualizacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atualizacao
        fields = ['id', 'autor_nome', 'autor_cargo', 'acao', 'recurso', 'descricao', 'criado_em']


class ConfigurarEmpresaSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=256)
    cnpj = serializers.CharField(max_length=18)

    def validate_cnpj(self, value):
        if not validator_cnpj.validate(value):
            raise serializers.ValidationError('CNPJ inválido.')
        value = validator_cnpj.mask(value)
        if Empresa.objects.filter(cnpj=value).exists():
            raise serializers.ValidationError('Empresa já cadastrada. Use a conta vinculada a ela ou o ajuste administrativo de contas existentes.')
        return value
