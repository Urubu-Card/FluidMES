import math
from django.utils import timezone
from django.db import transaction
from rest_framework import serializers
from .models import Receita, Pedido, OEERegistro, Parada, Solicitacao, LoteProducao


class ComponenteSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=80)
    quantidade_l = serializers.FloatField(min_value=0.000001, max_value=1000000)
    vazao_l_min = serializers.FloatField(min_value=0.000001, max_value=100000)

    def validate(self, attrs):
        if not all(math.isfinite(attrs[k]) for k in ("quantidade_l", "vazao_l_min")):
            raise serializers.ValidationError("Quantidades e vazões devem ser finitas.")
        return attrs


class ReceitaSerializer(serializers.ModelSerializer):
    componentes = ComponenteSerializer(many=True, required=False)
    volume_base_l = serializers.SerializerMethodField()

    class Meta:
        model = Receita
        exclude = ["empresa"]
        read_only_fields = ["versao"]
        extra_kwargs = {
            name: {"required": False}
            for name in ("ingrediente1", "ingrediente2", "ingrediente3", "tempo2")
        }

    def get_volume_base_l(self, obj):
        from .services.recipes import components

        return sum(p["quantidade_l"] for p in components(obj))

    def validate(self, attrs):
        parts = attrs.get(
            "componentes",
            (self.instance.componentes or None) if self.instance else None,
        )
        if parts is not None:
            if len(parts) not in (2, 3):
                raise serializers.ValidationError(
                    {"componentes": "A receita deve ter dois ou três ingredientes."}
                )
            if len({p["nome"].strip().casefold() for p in parts}) != len(parts):
                raise serializers.ValidationError(
                    {"componentes": "Use nomes distintos para os ingredientes."}
                )
            for index in range(3):
                attrs[f"ingrediente{index+1}"] = (
                    parts[index]["quantidade_l"] if index < len(parts) else 0
                )
            if len(parts) == 2:
                attrs["tempo2"] = 0
        for field in (
            "ingrediente1",
            "ingrediente2",
            "ingrediente3",
            "tempo1",
            "tempo2",
        ):
            value = attrs.get(field, getattr(self.instance, field, 0))
            if not math.isfinite(value) or value < 0 or value > 1000000:
                raise serializers.ValidationError(
                    {field: "Use um valor finito entre 0 e 1.000.000."}
                )
        if not self.instance:
            for field in ("ingrediente1", "ingrediente2", "ingrediente3", "tempo2"):
                attrs.setdefault(field, 0)
        return attrs

    @transaction.atomic
    def update(self, instance, validated_data):
        instance = Receita.objects.select_for_update().get(pk=instance.pk)
        if any(
            getattr(instance, key) != value for key, value in validated_data.items()
        ):
            validated_data["versao"] = instance.versao + 1
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        from .services.recipes import components

        result = super().to_representation(instance)
        result["componentes"] = components(instance)
        return result


class LoteSerializer(serializers.ModelSerializer):
    planta_nome = serializers.CharField(source="planta.nome", read_only=True)
    fase_atual = serializers.SerializerMethodField()

    class Meta:
        model = LoteProducao
        exclude = ["pedido"]

    def get_fase_atual(self, obj):
        if obj.status == "concluido":
            return "Concluído"
        if not obj.iniciado_em:
            return "Aguardando início"
        if obj.planta.suspensa_desde:
            return "Pausado · planta indisponível"
        if obj.comando_em:
            # Execução real: a etapa vem do CLP, não do relógio.
            controle = obj.planta.clp_controle()
            estado = controle.estado_tanque if controle else {}
            if not obj.ciclo_confirmado:
                return "START_CYCLE enviado · aguardando o CLP"
            if estado.get("etapa"):
                return f"Etapa {estado['etapa']} no CLP · nível {estado.get('nivel_atual', 0)}"
            return "Ciclo em execução no CLP"
        elapsed = max(
            0,
            (timezone.now() - obj.iniciado_em).total_seconds()
            - obj.pausa_acumulada_seg,
        )
        for step in obj.etapas:
            elapsed -= step["duracao_seg"]
            if elapsed < 0:
                return step["nome"]
        return "Finalizando ciclo"


class PedidosSerializer(serializers.ModelSerializer):
    em_pausa = serializers.BooleanField(read_only=True, default=False)
    plano = serializers.JSONField(source="plano_snapshot", read_only=True)
    lotes = serializers.SerializerMethodField()
    planta_preferida_nome = serializers.CharField(
        source="planta_preferida.nome", read_only=True, default=None
    )

    def get_lotes(self, obj):
        if getattr(self.context.get("view"), "action", None) == "list":
            return []
        return LoteSerializer(obj.lotes.all(), many=True).data

    receita_nome = serializers.SerializerMethodField()

    def get_receita_nome(self, obj):
        return obj.receita_snapshot.get("nome") or obj.receita.nome

    planta_nome = serializers.CharField(source="planta.nome", read_only=True)
    usuario_nome = serializers.SerializerMethodField()
    usuario_cargo = serializers.CharField(
        source="usuario.get_role_display", read_only=True
    )
    aprovado_por_nome = serializers.CharField(
        source="aprovado_por.first_name", read_only=True
    )
    simulado = serializers.SerializerMethodField()
    motivo_pausa = serializers.SerializerMethodField()

    def get_motivo_pausa(self, obj):
        if not getattr(obj, "em_pausa", False):
            return []
        from .services.production import motivo_pausa

        plantas = {
            lote.planta_id: lote.planta
            for lote in obj.lotes.all()
            if lote.status != "concluido" and lote.planta.suspensa_desde
        }
        return [
            {"planta": p.nome, "motivo": motivo_pausa(p) or "Planta indisponível"}
            for p in plantas.values()
        ]

    execucao_clp = serializers.SerializerMethodField()

    def get_execucao_clp(self, obj):
        """Plantas deste pedido que produzem de verdade pelo CLP (retrieve)."""
        if getattr(self.context.get("view"), "action", None) != "retrieve":
            return None
        from apps.plantas.serializers import controle_painel

        plantas = {lote.planta_id: lote.planta for lote in obj.lotes.all()}
        return [
            {"planta": planta.nome, **controle_painel(clp)}
            for planta in plantas.values()
            if (clp := planta.clp_controle())
        ]

    class Meta:
        model = Pedido
        fields = "__all__"
        read_only_fields = [
            "empresa",
            "usuario",
            "concluido_em",
            "tempo_ciclo_ideal_seg",
            "iniciado_em",
            "criado_em",
            "aprovado_em",
            "aprovado_por",
            "duracao_simulada_seg",
            "status",
            "aprovacao",
            "quantidade_boa",
            "receita_snapshot",
            "plano_snapshot",
            "planta_preferida",
        ]
        extra_kwargs = {"planta": {"required": False, "allow_null": True}}

    def to_representation(self, instance):
        result = super().to_representation(instance)
        if (
            getattr(self.context.get("view"), "action", None) == "retrieve"
            and instance.aprovacao == "aguardando"
        ):
            from .services.production import preview

            try:
                plan = preview(
                    instance.empresa_id,
                    instance.receita,
                    instance.quantidade,
                    instance.planta_preferida_id,
                    recipe_snapshot=instance.receita_snapshot or None,
                )
                result["plano"] = {k: v for k, v in plan.items() if k != "lotes"}
                result["lotes"] = plan["lotes"]
            except serializers.ValidationError as error:
                result["aviso_previsao"] = str(error.detail)
        return result

    def get_usuario_nome(self, obj):
        return (
            (obj.usuario.get_full_name() or obj.usuario.email)
            if obj.usuario
            else "Usuário removido"
        )

    def get_simulado(self, obj):
        from django.conf import settings

        return settings.SIMULACAO_PRODUCAO

    def validate(self, attrs):
        company = self.context["request"].user.empresa_id
        for field in ("receita", "planta"):
            value = attrs.get(field)
            if value and value.empresa_id != company:
                raise serializers.ValidationError(
                    {field: "Registro inválido para esta empresa."}
                )
        quantity = attrs.get("quantidade", getattr(self.instance, "quantidade", 0))
        if not math.isfinite(quantity) or quantity < 0.01 or quantity > 1000000:
            raise serializers.ValidationError(
                {"quantidade": "A quantidade deve ser positiva e finita."}
            )
        return attrs


class SolicitacaoSerializer(serializers.ModelSerializer):
    autor_nome = serializers.SerializerMethodField()
    autor_cargo = serializers.CharField(source="autor.get_role_display", read_only=True)

    class Meta:
        model = Solicitacao
        fields = [
            "id",
            "tipo",
            "dados",
            "status",
            "autor_nome",
            "autor_cargo",
            "autor",
            "criado_em",
            "decidido_em",
            "resultado_id",
        ]

    def get_autor_nome(self, obj):
        return (
            (obj.autor.get_full_name() or obj.autor.email)
            if obj.autor
            else "Usuário removido"
        )


class OEERegistroSerializer(serializers.ModelSerializer):
    planta_nome = serializers.CharField(source="planta.nome", read_only=True)
    disponibilidade = serializers.FloatField(read_only=True)
    performance = serializers.FloatField(read_only=True)
    qualidade = serializers.FloatField(read_only=True)
    oee = serializers.FloatField(read_only=True)

    class Meta:
        model = OEERegistro
        fields = "__all__"


class ParadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parada
        fields = "__all__"

    def validate(self, attrs):
        plant = attrs.get("planta", getattr(self.instance, "planta", None))
        if plant and plant.empresa_id != self.context["request"].user.empresa_id:
            raise serializers.ValidationError("Planta inválida.")
        start = attrs.get("inicio", getattr(self.instance, "inicio", None))
        end = attrs.get("fim", getattr(self.instance, "fim", None))
        if end and start and end < start:
            raise serializers.ValidationError("Fim anterior ao início.")
        return attrs
