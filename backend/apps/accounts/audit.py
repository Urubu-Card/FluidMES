from .models import Atualizacao

def record(actor, company, action, resource, description):
    Atualizacao.objects.create(
        empresa_id=company, autor=actor,
        autor_nome=(actor.get_full_name() or actor.email) if actor else 'Sistema',
        autor_cargo=actor.get_role_display() if actor else 'Automação',
        acao=action, recurso=resource, descricao=str(description)[:500])

class AuditMixin:
    """Audit API mutations in the same transaction as the change."""
    def perform_create(self, serializer):
        from django.db import transaction
        with transaction.atomic():
            super().perform_create(serializer)
            record(self.request.user, self.request.user.empresa_id, 'criou', self.audit_resource, str(serializer.instance))
    def perform_update(self, serializer):
        from django.db import transaction
        with transaction.atomic():
            super().perform_update(serializer)
            record(self.request.user, self.request.user.empresa_id, 'editou', self.audit_resource, str(serializer.instance))
    def perform_destroy(self, instance):
        from django.db import transaction
        with transaction.atomic():
            label = str(instance)
            super().perform_destroy(instance)
            record(self.request.user, self.request.user.empresa_id, 'excluiu', self.audit_resource, label)
