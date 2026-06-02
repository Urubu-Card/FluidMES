
from django.urls import path , include
from .views import Clp , Autenticacao , Inicio

urlpatterns = [
    path("",            Inicio.landing_page,               name="clp_test"),
    path("status/",     Clp.status,                  name="status_coil"),
    path("cadastro/",   Autenticacao.Cadastrar,      name="register"),
    path("login/",      Autenticacao.Login,          name="login")
]
