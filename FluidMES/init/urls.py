
from django.urls import path , include
from .views import teste_clp ,status_coil

urlpatterns = [
    path("",teste_clp,name="clp_test"),
     path("status-coil/", status_coil, name="status_coil")
    
]
