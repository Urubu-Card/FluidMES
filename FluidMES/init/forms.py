from django import forms 
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.password_validation import validate_password
from validate_docbr import CPF,CNPJ

validator_CPF = CPF()
 
validator_CNPJ = CNPJ()

class Cadastro(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username')
        self.fields['password1'].widget.attrs.update({"placeholder":"Senha"})
        self.fields['password2'].widget.attrs.update({"placeholder":"Confirme sua senha"})
        self.fields['nome']         = forms.CharField(max_length=250,widget=forms.TextInput(attrs={"placeholder":"Nome"}))
        self.fields['email']        = forms.EmailField(widget=forms.EmailInput({"placeholder":"E-mail"}))
        self.fields['telefone']     = forms.CharField(max_length=15,widget=forms.TextInput(attrs={'data-mask': '(00) 00000-0000',"placeholder":"Telefone"}))
        self.fields['cpf']          = forms.CharField(max_length=14,widget=forms.TextInput(attrs={"data-mask":"000.000.000-00   ",'placeholder':"CPF"}))
        self.fields['nomeEmpresa']  = forms.CharField(max_length=250,widget=forms.TextInput(attrs={"placeholder":"Nome da Empresa   "}))
        self.fields['cnpj']         = forms.CharField(max_length=18,widget=forms.TextInput(attrs={"data-mask":"00.000.000/0000-00","placeholder":"CNPJ"}))
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
    
        if not validator_CPF.validate(cpf):
            raise forms.ValidationError("CPF invalido")
    
        return cpf
    
    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
    
        if not validator_CNPJ.validate(cnpj):
            raise forms.ValidationError("CNPJ invalido")
        
    
        return cnpj