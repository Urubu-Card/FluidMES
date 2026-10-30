from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection

def health(request):
    try:
        with connection.cursor() as cursor: cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status":"unavailable"}, status=503)
    response = JsonResponse({"status":"ok"})
    response["Cache-Control"] = "no-store"
    return response


urlpatterns = [
    path('api/health/', health),
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('', include('apps.plantas.urls')),
    path('', include('apps.producao.urls')),
]
