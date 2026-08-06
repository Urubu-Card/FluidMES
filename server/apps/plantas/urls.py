from django.urls import path
from apps.plantas import views

urlpatterns = [
    path('api/plantas/',   views.PlantaListView.as_view()),
    path('api/clps/',       views.ClpListView.as_view() )
]
