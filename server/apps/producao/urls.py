from django.urls import path,include
from apps.producao import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'pedidos' ,    views.PedidosView,  basename='pedido')
urlpatterns = [
    path('api/', include(router.urls)),
    
]