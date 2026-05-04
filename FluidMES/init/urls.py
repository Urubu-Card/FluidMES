
from django.urls import path , include
from .views import teste_clp ,status

urlpatterns = [
    path("",teste_clp,name="clp_test"),
     path("status/", status, name="status_coil")
    
]
