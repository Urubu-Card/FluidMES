from django.urls    import path,include
from rest_framework.routers import SimpleRouter
from apps.plantas   import views

router = SimpleRouter()
router.register(r'plantas' , views.PlantasView, basename='planta')

urlpatterns = [
    # path('api/plantas/',    views.PlantaListView.as_view()),
    # path('api/clps/',       views.ClpListView.as_view() ),
    # path('api/sensores/',   views.SensoresListView.as_view() )
    path("api/",include(router.urls))
]
