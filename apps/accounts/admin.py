from django.contrib import admin
from .models import Empresa, Usuarios , PasswordResetToken

admin.site.register(Empresa)
admin.site.register(Usuarios)

