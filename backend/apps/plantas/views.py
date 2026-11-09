from collections.abc import Mapping

from django.db import transaction
from django.db.models import Prefetch, Sum, Q, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from asgiref.sync import async_to_sync
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from apps.accounts.permissions import RequestCreateAccess, OwnerAccess
from apps.accounts.audit import AuditMixin, record
from apps.producao.models import Pedido, OEERegistro, LoteProducao
from apps.producao.workflow import enqueue_request
from apps.producao.simulation_api import SimulationMutationMixin
from services.clp_control import EscritaRecusada
from services.modbus_map import MODO_MES, TAGS, modo_label, tanque_da_tag
from .models import Planta, Clp, Sensor, Leitura
from .mapeamento import aplicar
from .sensor_io import ERROS_MODBUS, consultar, ler_modo
from .serializers import PlantaSerializer, ClpSerializer, SensorSerializer


class PlantasView(SimulationMutationMixin, AuditMixin, ModelViewSet):
    serializer_class = PlantaSerializer
    permission_classes = [RequestCreateAccess]
    audit_resource = "planta"

    def get_queryset(self):
        return (
            Planta.objects.filter(empresa=self.request.user.empresa)
            .annotate(
                produzido_lotes=Coalesce(
                    Sum("lotes__quantidade", filter=Q(lotes__status="concluido")),
                    Value(0.0),
                ),
                planejado_lotes=Coalesce(Sum("lotes__quantidade"), Value(0.0)),
            )
            .order_by("idplanta")
            .prefetch_related(
                Prefetch(
                    "pedidos",
                    queryset=Pedido.objects.select_related("receita").order_by(
                        "-idpedido"
                    ),
                    to_attr="card_orders",
                ),
                Prefetch(
                    "oee_registros",
                    queryset=OEERegistro.objects.order_by("-data")[:1],
                    to_attr="card_oee",
                ),
                Prefetch(
                    "clps", queryset=Clp.objects.order_by("idclp"), to_attr="card_clps"
                ),
                Prefetch(
                    "lotes",
                    queryset=LoteProducao.objects.exclude(status="concluido")
                    .select_related("pedido")
                    .order_by("inicio_previsto"),
                    to_attr="card_lots",
                ),
            )
        )

    def create(self, request, *args, **kwargs):
        if request.user.role == 3:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return enqueue_request(request, "planta", serializer)
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa)
        record(
            self.request.user,
            self.request.user.empresa_id,
            "criou",
            "planta",
            serializer.instance.nome,
        )

    @transaction.atomic
    def perform_destroy(self, instance):
        if instance.pedidos.exists() or instance.lotes.exists():
            raise ValidationError("Planta possui pedidos; exclusão não permitida.")
        label = instance.nome
        instance.delete()
        record(
            self.request.user, self.request.user.empresa_id, "excluiu", "planta", label
        )


class ClpView(AuditMixin, ModelViewSet):
    serializer_class = ClpSerializer
    permission_classes = [OwnerAccess]
    audit_resource = "CLP"

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def aplicar_mapeamento(self, request, pk=None):
        clp = get_object_or_404(
            self.get_queryset().select_for_update(of=("self",)), pk=pk
        )
        self.check_object_permissions(request, clp)
        novos, existentes = aplicar(clp)
        if novos:
            record(
                request.user,
                request.user.empresa_id,
                "aplicou",
                "mapeamento Modbus",
                f"{clp.nome} · {novos} tags cadastradas",
            )
        return Response({"cadastradas": novos, "existentes": existentes})

    @action(detail=True, methods=["post"])
    def testar(self, request, pk=None):
        from services.clp_probe import probe

        clp = self.get_object()
        sensor = (
            clp.sensores.order_by("pk")
            .values("nome", "tipo_registro", "endereco")
            .first()
        )
        result = async_to_sync(probe)(clp.ip, clp.porta, sensor)
        clp.status = (
            "online"
            if result["leitura_validada"]
            else "conectado" if result["conectado"] else "offline"
        )
        fields = ["status"]
        if result["leitura_validada"]:
            clp.ultima_comunicacao = timezone.now()
            fields.append("ultima_comunicacao")
        clp.save(update_fields=fields)
        result["ultima_comunicacao"] = clp.ultima_comunicacao
        return Response(result)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._mapear(serializer.instance)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._mapear(serializer.instance)

    def _mapear(self, clp):
        """CLP de produção (TK1/TK2) já sai com as tags da planilha cadastradas."""
        if not clp.tanque:
            return
        try:
            novos, _ = aplicar(clp)
        except ValidationError:
            return  # Conflito com sensores antigos: o botão do mapa mostra o motivo.
        if novos:
            record(
                self.request.user, self.request.user.empresa_id, "aplicou",
                "mapeamento Modbus", f"{clp.nome} · {novos} tags cadastradas",
            )

    def get_queryset(self):
        return Clp.objects.filter(
            planta__empresa=self.request.user.empresa
        ).select_related("planta")


class SensoresView(AuditMixin, ModelViewSet):
    serializer_class = SensorSerializer
    permission_classes = [OwnerAccess]
    audit_resource = "sensor"

    def get_queryset(self):
        ultima = Leitura.objects.filter(sensor_id=OuterRef("pk")).order_by(
            "-timestamp", "-pk"
        )
        return (
            Sensor.objects.filter(clp__planta__empresa=self.request.user.empresa)
            .select_related("clp")
            .annotate(
                valor_atual=Subquery(ultima.values("valor")[:1]),
                lido_em=Subquery(ultima.values("timestamp")[:1]),
            )
            .order_by("pk")
        )

    def salvar_leitura(self, sensor, valor):
        if valor is not None:
            leitura = Leitura.objects.create(sensor=sensor, valor=valor)
            Clp.objects.filter(pk=sensor.clp_id).update(
                status="online", ultima_comunicacao=leitura.timestamp
            )

    @action(detail=False, methods=["get"])
    def unidades(self, request):
        return Response(Sensor.UNIDADES_POR_TIPO)

    @action(detail=True, methods=["post"])
    def ler(self, request, pk=None):
        sensor = self.get_object()
        if not sensor.clp.ativo:
            raise ValidationError({"detail": "O CLP está desativado."})
        try:
            valor = async_to_sync(consultar)(sensor)
        except ERROS_MODBUS:
            return Response(
                {"detail": "Não foi possível ler este endereço no CLP."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        self.salvar_leitura(sensor, valor)
        return Response({"detail": "Leitura atualizada.", "valor": valor})

    @action(detail=True, methods=["post"])
    def escrever(self, request, pk=None):
        sensor = self.get_object()
        if not sensor.pode_escrever:
            return Response(
                {"detail": "A escrita está bloqueada para este sensor ou CLP."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # MODO pertence à planta; e fora do modo 2 o MES não comanda o tanque.
        tanque = tanque_da_tag(sensor.nome) or sensor.clp.tanque
        if tanque_da_tag(sensor.nome) and sensor.nome.endswith(".MODO"):
            return Response(
                {"detail": "O modo é escolhido na planta. O MES apenas o lê."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if tanque:
            try:
                modo = async_to_sync(ler_modo)(sensor.clp, tanque)
            except ERROS_MODBUS:
                return Response(
                    {"detail": "Não foi possível ler o modo da planta. Nada foi enviado."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            if modo != MODO_MES:
                record(
                    request.user, request.user.empresa_id, "teve comando bloqueado",
                    "Modbus", f"{sensor.clp} · {sensor.nome} · modo {modo}",
                )
                return Response(
                    {
                        "detail": (
                            f"Planta em modo {modo} ({modo_label(modo)}). "
                            "O MES só envia comandos com a planta no modo 2."
                        ),
                        "modo": modo,
                    },
                    status=status.HTTP_423_LOCKED,
                )
        valor = request.data.get("valor") if isinstance(request.data, Mapping) else None
        if sensor.tipo_registro == Sensor.TipoRegistro.COIL:
            if type(valor) is not bool:
                raise ValidationError({"valor": "Informe true ou false para a coil."})
        elif type(valor) is not int or not 0 <= valor <= 65535:
            raise ValidationError({"valor": "Informe um inteiro de 0 a 65535."})
        elif not sensor.minimo <= valor <= sensor.maximo:
            raise ValidationError({
                "valor": f"Use um valor entre {sensor.minimo:g} e {sensor.maximo:g}."
            })

        descricao = f"{sensor.clp} · {sensor.nome} · offset {sensor.endereco} · valor {valor}"
        try:
            leitura = async_to_sync(consultar)(sensor, comando=valor)
        except EscritaRecusada as erro:
            record(request.user, request.user.empresa_id, "teve comando recusado", "Modbus", descricao)
            return Response(
                {"detail": f"O CLP recusou o comando. {erro}."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except ERROS_MODBUS:
            record(request.user, request.user.empresa_id, "enviou sem confirmação", "Modbus", descricao)
            return Response(
                {"detail": "Sem confirmação do CLP. Consulte o estado antes de reenviar."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        record(request.user, request.user.empresa_id, "confirmou escrita", "Modbus", descricao)
        self.salvar_leitura(sensor, leitura)
        return Response({
            "detail": (
                "Comando confirmado pelo CLP. Leitura de retorno indisponível."
                if leitura is None else "Comando confirmado pelo CLP."
            ),
            "valor": leitura,
        })
