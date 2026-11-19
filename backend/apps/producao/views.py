from django.conf import settings
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from apps.accounts.permissions import (
    CompanyAccess,
    CompanyMember,
    RequestCreateAccess,
    OwnerAccess,
)
from apps.accounts.audit import AuditMixin, record
from .models import Pedido, Receita, OEERegistro, Parada, Solicitacao
from .serializers import (
    PedidosSerializer,
    ReceitaSerializer,
    OEERegistroSerializer,
    ParadaSerializer,
    SolicitacaoSerializer,
)
from .workflow import advance_plant, decide_order, decide_request, enqueue_request
from .simulation_api import SimulationMutationMixin


class ReceitasView(AuditMixin, ModelViewSet):
    permission_classes = [RequestCreateAccess]
    serializer_class = ReceitaSerializer
    audit_resource = "receita"

    def get_queryset(self):
        return Receita.objects.filter(empresa=self.request.user.empresa).order_by(
            "idreceita"
        )

    def create(self, request, *args, **kwargs):
        if request.user.role == 3:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return enqueue_request(request, "receita", serializer)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)
        record(
            self.request.user,
            self.request.user.empresa_id,
            "criou",
            "receita",
            serializer.instance.nome,
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        try:
            label = instance.nome
            instance.delete()
            record(
                self.request.user,
                self.request.user.empresa_id,
                "excluiu",
                "receita",
                label,
            )
        except ProtectedError:
            raise ValidationError(
                "Receita utilizada em pedidos; exclusão não permitida."
            )


class PedidosView(SimulationMutationMixin, ModelViewSet):
    permission_classes = [CompanyMember]
    serializer_class = PedidosSerializer

    @action(detail=False, methods=["post"])
    def prever(self, request):
        from .services.production import preview
        from .services.recipes import snapshot

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        recipe = data["receita"]
        return Response(
            preview(
                request.user.empresa_id,
                recipe,
                data["quantidade"],
                getattr(data.get("planta"), "pk", None),
                recipe_snapshot=snapshot(recipe),
            )
        )

    def get_queryset(self):
        from django.db.models import Exists, OuterRef
        from .models import LoteProducao

        query = (
            Pedido.objects.annotate(
                em_pausa=Exists(
                    LoteProducao.objects.filter(
                        pedido_id=OuterRef("pk"), planta__suspensa_desde__isnull=False
                    ).exclude(status="concluido")
                )
            )
            .filter(empresa=self.request.user.empresa)
            .select_related("receita", "planta", "usuario", "aprovado_por")
            .order_by("-criado_em", "-idpedido")
        )
        if self.action != "list":
            from django.db.models import Prefetch
            from .models import LoteProducao

            query = query.prefetch_related(
                Prefetch(
                    "lotes", queryset=LoteProducao.objects.select_related("planta")
                )
            )
        return (
            query.filter(usuario=self.request.user)
            if self.request.user.role == 3
            else query
        )

    @transaction.atomic
    def perform_create(self, serializer):
        from apps.plantas.models import Planta

        plant = serializer.validated_data.get("planta")
        preferred = plant
        if plant is None:
            plant = (
                Planta.objects.filter(empresa=self.request.user.empresa)
                .order_by("pk")
                .first()
            )
        if plant is None:
            raise ValidationError("Cadastre uma planta antes de criar pedidos.")
        from .services.recipes import snapshot
        from .services.production import preview, reserve

        recipe_snapshot = snapshot(serializer.validated_data["receita"])
        estimate = preview(
            self.request.user.empresa_id,
            serializer.validated_data["receita"],
            serializer.validated_data["quantidade"],
            getattr(preferred, "pk", None),
            recipe_snapshot=recipe_snapshot,
        )
        list(
            Planta.objects.select_for_update()
            .filter(empresa=self.request.user.empresa)
            .order_by("pk")
        )
        manager = self.request.user.role in (1, 2)
        order = serializer.save(
            empresa=self.request.user.empresa,
            usuario=self.request.user,
            planta=plant,
            planta_preferida=preferred,
            receita_snapshot=recipe_snapshot,
            plano_snapshot={k: v for k, v in estimate.items() if k != "lotes"},
            aprovacao="aprovado" if manager else "aguardando",
            aprovado_por=self.request.user if manager else None,
            aprovado_em=timezone.now() if manager else None,
        )
        record(
            self.request.user,
            self.request.user.empresa_id,
            "criou",
            "pedido de produção",
            f"Pedido #{order.pk} · {order.receita.nome}",
        )
        if manager:
            reserve(order)
            order.refresh_from_db()

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        if request.user.role != 1:
            raise PermissionDenied(
                "Somente o Preposto pode corrigir pedidos pendentes."
            )
        order = self.get_object()
        from apps.plantas.models import Planta

        Planta.objects.select_for_update().get(pk=order.planta_id)
        order.refresh_from_db()
        if order.status != "pendente" or order.aprovacao != "aguardando":
            raise ValidationError(
                "Somente pedidos aguardando aprovação podem ser editados."
            )
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        from .services.recipes import snapshot

        recipe = serializer.validated_data.get("receita", serializer.instance.receita)
        preferred = serializer.validated_data.get(
            "planta", serializer.instance.planta_preferida
        )
        if serializer.validated_data.get("planta") is None:
            serializer.validated_data.pop("planta", None)
        order = serializer.save(
            receita_snapshot=snapshot(recipe), planta_preferida=preferred
        )
        record(
            self.request.user,
            self.request.user.empresa_id,
            "editou",
            "pedido de produção",
            f"Pedido #{order.pk} · {order.receita.nome}",
        )

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 1:
            raise PermissionDenied("Somente o Preposto pode excluir pedidos pendentes.")
        instance = self.get_object()
        if instance.status != "pendente" or instance.aprovacao != "aguardando":
            raise ValidationError("Este pedido não pode ser excluído.")
        with transaction.atomic():
            label = f"Pedido #{instance.pk}"
            instance.delete()
            record(
                request.user,
                request.user.empresa_id,
                "excluiu",
                "pedido de produção",
                label,
            )
        return Response(status=204)

    @action(detail=True, methods=["post"])
    def aprovar(self, request, pk=None):
        return self._decide(request, True)

    @action(detail=True, methods=["post"])
    def recusar(self, request, pk=None):
        return self._decide(request, False)

    def _decide(self, request, approved):
        if request.user.role not in (1, 2):
            raise PermissionDenied("Somente Chefes e Preposto podem analisar pedidos.")
        order = self.get_object()
        return Response(
            self.get_serializer(decide_order(order.pk, request.user, approved)).data
        )


class SolicitacoesView(ReadOnlyModelViewSet):
    permission_classes = [CompanyMember]
    serializer_class = SolicitacaoSerializer

    def get_queryset(self):
        query = Solicitacao.objects.filter(
            empresa=self.request.user.empresa
        ).select_related("autor", "decidido_por")
        return (
            query.filter(autor=self.request.user)
            if self.request.user.role == 3
            else query
        )

    @action(detail=True, methods=["post"])
    def aprovar(self, request, pk=None):
        return self._decide(request, True)

    @action(detail=True, methods=["post"])
    def recusar(self, request, pk=None):
        return self._decide(request, False)

    def _decide(self, request, approved):
        if request.user.role not in (1, 2):
            raise PermissionDenied(
                "Somente Chefes e Preposto podem analisar solicitações."
            )
        req = self.get_object()
        return Response(
            self.get_serializer(decide_request(req.pk, request.user, approved)).data
        )


class RendimentosView(ReadOnlyModelViewSet):
    permission_classes = [OwnerAccess]
    serializer_class = OEERegistroSerializer

    def get_queryset(self):
        return OEERegistro.objects.filter(
            planta__empresa=self.request.user.empresa
        ).select_related("planta")


class ParadasView(SimulationMutationMixin, AuditMixin, ModelViewSet):
    permission_classes = [OwnerAccess]
    serializer_class = ParadaSerializer
    audit_resource = "parada"

    def get_queryset(self):
        return Parada.objects.filter(
            planta__empresa=self.request.user.empresa
        ).order_by("-inicio")
