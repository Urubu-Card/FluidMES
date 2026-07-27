from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('api/cadastro/',       views.CadastroView.as_view(),          name='api/register'),
    path('api/login/',          views.LoginView.as_view(),             name='api/login'),
    path('api/logout/',         views.LogoutView.as_view(),            name='api/logout'),
    path('api/me/',             views.MeView.as_view(),                name='api/me'),
    path('api/token/refresh/',  TokenRefreshView.as_view(),            name='api/refresh')
]
