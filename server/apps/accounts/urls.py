from django.urls import path , include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register(r'funcionarios' , views.FuncionariosView, basename='funcionario')


urlpatterns = [
    path('api/login/',                      views.LoginView.as_view(),                               ),
    path('api/cadastro/',                   views.CadastroView.as_view(),                            ),
    path('api/me/',                         views.MeView.as_view(),                                  ),
    path('api/logout/',                     views.LogoutView.as_view(),                              ),                       
    path('api/password-reset/',             views.PasswordResetRequestView.as_view(),                ),
    path('api/password-reset/confirm/',     views.PasswordRestConfirmView.as_view(),                 ),
    path('api/token/refresh/',              views.TokenRefreshCookieView.as_view(),                  ),
    
    
    
    path('api/',include(router.urls))
]
