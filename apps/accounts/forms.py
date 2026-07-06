from django import forms
from django.contrib.auth.forms import UserCreationForm
from validate_docbr import CPF, CNPJ
from django.contrib.auth import authenticate
from .models import Empresa, Usuarios

validator_CPF  = CPF()
validator_CNPJ = CNPJ()


class Cadastro(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Senha'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirme sua senha'})
        self.fields['nome']        = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'placeholder': 'Nome'}))
        self.fields['email']       = forms.EmailField(widget=forms.EmailInput({'placeholder': 'E-mail'}))
        self.fields['cpf']         = forms.CharField(max_length=14, widget=forms.TextInput(attrs={'data-mask': '000.000.000-00', 'placeholder': 'CPF'}))
        self.fields['nomeEmpresa'] = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'placeholder': 'Nome da Empresa'}))
        self.fields['cnpj']        = forms.CharField(max_length=18, widget=forms.TextInput(attrs={'data-mask': '00.000.000/0000-00', 'placeholder': 'CNPJ'}))

    class Meta(UserCreationForm.Meta):
        model  = Usuarios
        fields = ['email', 'nome', 'cpf', 'password1', 'password2']

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not validator_CPF.validate(cpf):
            raise forms.ValidationError('CPF inválido')
        return cpf

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if not validator_CNPJ.validate(cnpj):
            raise forms.ValidationError('CNPJ inválido')
        return cnpj

    def save(self):
        empresa = Empresa.objects.create(
            nome=self.cleaned_data['nomeEmpresa'],
            cnpj=self.cleaned_data['cnpj'],
        )
        return Usuarios.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            nome=self.cleaned_data['nome'],
            cpf=self.cleaned_data['cpf'],
            empresa=empresa,
        )


class Login(forms.Form):
    usuario  = forms.CharField(max_length=150, widget=forms.TextInput({'placeholder': 'E-mail ou CPF'}))
    password = forms.CharField(max_length=250, widget=forms.PasswordInput(attrs={'placeholder': 'Senha'}))

    def Autenticar(self, request):
        return authenticate(
            request,
            username=self.cleaned_data.get('usuario'),
            password=self.cleaned_data.get('password'),
        )
