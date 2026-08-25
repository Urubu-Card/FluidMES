from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('api/login/',                      views.LoginView.as_view(),                               ),
    path('api/cadastro/',                   views.CadastroView.as_view(),                            ),
    path('api/me/',                         views.MeView.as_view(),                                  ),
    path('api/logout/',                     views.LogoutView.as_view(),                              ),
    path('api/token/refresh/',              TokenRefreshView.as_view(),                              ),
    
]
