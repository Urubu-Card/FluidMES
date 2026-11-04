from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Empresa, Usuarios, Preferencias, Atualizacao

class AccountCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuarios
        fields = ('email','first_name','cpf','empresa','role')

class AccountChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Usuarios
        fields = '__all__'

@admin.register(Usuarios)
class AccountAdmin(UserAdmin):
    form = AccountChangeForm
    add_form = AccountCreationForm
    ordering = ('email',)
    list_display = ('email','first_name','empresa','role','is_active','is_staff')
    search_fields = ('email','cpf','first_name','last_name')
    fieldsets = ((None, {'fields':('email','password')}),
                 ('Conta', {'fields':('first_name','last_name','cpf','empresa','role')}),
                 ('Permissões', {'fields':('is_active','is_staff','is_superuser','groups','user_permissions')}),
                 ('Datas', {'fields':('last_login','date_joined')}))
    add_fieldsets = ((None, {'fields':('email','first_name','cpf','empresa','role','password1','password2')}),)

admin.site.register(Empresa)
admin.site.register(Preferencias)

@admin.register(Atualizacao)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('criado_em','autor_nome','acao','recurso','empresa')
    readonly_fields = tuple(f.name for f in Atualizacao._meta.fields)
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

admin.site.site_header = 'FluidMES — Administração'
admin.site.site_title = 'FluidMES Admin'
