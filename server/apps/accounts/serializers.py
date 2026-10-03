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
    first_name          = serializers.CharField(max_length=256)
    last_name           = serializers.CharField(max_length=256)
    email               = serializers.EmailField()
    cpf                 = serializers.CharField(max_length=14)
    password            = serializers.CharField(write_only=True,validators = [validate_password])
    nomeEmpresa         = serializers.CharField(max_length=256)
    cnpj                = serializers.CharField(max_length=18)
    
    
    def validate_cpf(self, value):
        if not validator_cpf.validate(value):
            raise serializers.ValidationError("CPF Invalido")
        return value
    
    def validate_cnpj(self, value):
        if not validator_cnpj.validate(value):
            raise serializers.ValidationError("CNPJ Invalido")
        return value

    
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
            empresa    = empresa,)
        
        

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
    
    class Meta:
        model  = Usuarios
        fields = ['id', 'email', 'first_name','last_name', 'cpf', 'role','is_active' ,'empresa']
        read_only_fields = ['id']