from django import forms 
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.password_validation import validate_password


class Cadastro(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({"placeholder":"Username"})
        self.fields['email']    = forms.EmailField(widget=forms.EmailInput({"placeholder":"E-mail"}))
        self.fields['password1'].widget.attrs.update({"placeholder":"Senha"})
        self.fields['password2'].widget.attrs.update({"placeholder":"Confirme sua senha"})
        self.fields['telefone'] = forms.CharField(max_length=15,widget=forms.TextInput(attrs={'data-mask': '(00) 00000-0000',"placeholder":"Telefone"}))
        #self.fields['cpf']      = forms
        