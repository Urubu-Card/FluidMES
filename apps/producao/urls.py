from django.urls import path
from . import views

urlpatterns = [
    path('pedidos/', views.pedidos, name='pedidos'),
    path('rendimento/', views.rendimento, name='rendimento'),
    path('receitas/', views.receitas, name='receitas'),
]