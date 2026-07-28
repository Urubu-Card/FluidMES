from django.urls import path
from . import views

urlpatterns = [
    path('plantas/',   views.plantas,    name='plantas'),
    path('home/', views.teste_clp,  name='home'),
    path('status/',    views.status_clp, name='status_coil'),
]
