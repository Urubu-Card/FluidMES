from django.contrib import admin
from .models import Pedido, Receita, LoteProducao, Solicitacao, OEERegistro, Parada

class ProductionRecordAdmin(admin.ModelAdmin):
    """Inspect operational records without bypassing scheduling/approval services."""
    def get_readonly_fields(self, request, obj=None):
        return tuple(f.name for f in self.model._meta.fields)
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

for model in (Pedido, Receita, LoteProducao, Solicitacao, OEERegistro, Parada):
    admin.site.register(model, ProductionRecordAdmin)
