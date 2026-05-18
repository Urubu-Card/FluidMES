
from django.urls import path , include
from .views import Clp , Cadastro

urlpatterns = [
    path("",            Clp.teste_clp,      name="clp_test"),
    path("status/",     Clp.status,         name="status_coil"),
    path("cadastro/",   Cadastro.Page,      name="register")
    
]
