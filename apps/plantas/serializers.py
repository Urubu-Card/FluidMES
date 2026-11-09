import math
from django.utils import timezone
from rest_framework import serializers
from services.modbus_map import STATUS_CICLO, modo_label
from .models import Planta, Clp, Sensor


def controle_painel(clp, offline=False):
    """Resumo do tanque para os cards: modo, etapa, nível e se o MES pode comandar."""
    if clp is None:
        return None
    estado = clp.estado_tanque or {}
    modo = estado.get("modo")
    if offline or modo is None:
        motivo = "Sem leitura recente do CLP."
    elif not clp.mes_liberado:
        motivo = (
            f"Modo {modo} · {modo_label(modo)}. "
            "O MES só comanda com a planta no modo 2."
        )
    elif not clp.escrita_habilitada:
        motivo = "Comandos Modbus desabilitados neste CLP."
    else:
        motivo = ""
    return {
        "clp": clp.pk,
        "tanque": clp.tanque,
        "modo": modo,
        "modo_label": modo_label(modo) if modo is not None else None,
        "mes_liberado": not motivo,
        "motivo": motivo,
        "etapa": estado.get("etapa"),
        "nivel_atual": estado.get("nivel_atual"),
        "niveis": estado.get("niveis"),
        "tempos": estado.get("tempos"),
        "status_ciclo": estado.get("status"),
        "status_ciclo_label": STATUS_CICLO.get(estado.get("status")),
        "lido_em": estado.get("lido_em"),
    }


class PlantaSerializer(serializers.ModelSerializer):
    painel = serializers.SerializerMethodField()

    def get_painel(self, obj):
        if not hasattr(obj, "card_orders"):
            return None
        orders = [order for order in obj.card_orders if not order.receita_snapshot]
        lots = getattr(obj, "card_lots", [])
        running_lot = next(
            (batch for batch in lots if batch.status == "em_andamento"), None
        )
        running = next(
            (order for order in orders if order.status == "em_andamento"), None
        )
        latest = obj.card_oee[0] if obj.card_oee else None
        clps = [clp for clp in obj.card_clps if clp.ativo]
        offline = any(
            clp.status != "online"
            or not clp.ultima_comunicacao
            or (timezone.now() - clp.ultima_comunicacao).total_seconds() > 15
            for clp in clps
        )
        from apps.producao.models import Parada

        stopped = Parada.objects.filter(planta=obj, fim__isnull=True).exists()
        controle = controle_painel(obj.clp_controle(clps), offline)
        return {
            "controle": controle,
            "status": (
                "parada"
                if stopped
                else (
                    "offline"
                    if offline
                    else (
                        "produzindo"
                        if running or running_lot
                        else (
                            "bloqueada"
                            if controle and not controle["mes_liberado"]
                            else "disponivel"
                        )
                    )
                )
            ),
            "receita": (
                running_lot.pedido.receita_snapshot["nome"]
                if running_lot
                else running.receita.nome if running else None
            ),
            "pedido": (
                running_lot.pedido_id
                if running_lot
                else running.pk if running else None
            ),
            "iniciado_em": (
                running_lot.iniciado_em
                if running_lot
                else running.iniciado_em if running else None
            ),
            "duracao_seg": (
                running_lot.setup_seg + running_lot.duracao_producao_seg
                if running_lot
                else running.duracao_simulada_seg if running else None
            ),
            "quantidade_produzida": sum(
                o.quantidade for o in orders if o.status == "concluido"
            )
            + getattr(obj, "produzido_lotes", 0),
            "quantidade_planejada": sum(
                o.quantidade
                for o in orders
                if o.aprovacao == "aprovado" and o.status != "cancelado"
            )
            + getattr(obj, "planejado_lotes", 0),
            "oee": latest.oee if latest else None,
            "oee_data": latest.data if latest else None,
            "fila": sum(
                o.status == "pendente" and o.aprovacao == "aprovado" for o in orders
            )
            + sum(b.status == "planejado" for b in lots),
        }

    def validate(self, attrs):
        if (
            self.instance
            and "capacidade_l" in attrs
            and self.instance.lotes.exclude(status="concluido")
            .filter(quantidade__gt=attrs["capacidade_l"])
            .exists()
        ):
            raise serializers.ValidationError(
                {
                    "capacidade_l": "Há ciclos programados maiores que esta capacidade. Preserve a capacidade até concluir os ciclos."
                }
            )
        return attrs

    def validate_capacidade_l(self, value):
        if not math.isfinite(value) or not 0.01 <= value <= 1000000:
            raise serializers.ValidationError(
                "A capacidade deve estar entre 0,01 e 1.000.000 L."
            )
        return value

    def validate_tempo_reset_seg(self, value):
        if not math.isfinite(value) or not 0 <= value <= 604800:
            raise serializers.ValidationError(
                "Informe um tempo de reset entre 0 e 604.800 segundos."
            )
        return value

    class Meta:
        model = Planta
        fields = [
            "idplanta",
            "uuid",
            "nome",
            "localizacao",
            "capacidade_l",
            "tempo_reset_seg",
            "painel",
        ]
        read_only_fields = ["idplanta", "uuid"]


class ClpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clp
        fields = [
            "idclp",
            "nome",
            "ip",
            "porta",
            "ativo",
            "escrita_habilitada",
            "status",
            "ultima_comunicacao",
            "planta",
            "tanque",
            "controle",
        ]
        read_only_fields = ["status", "ultima_comunicacao"]

    controle = serializers.SerializerMethodField()

    def get_controle(self, obj):
        return controle_painel(obj) if obj.tanque else None

    def validate_planta(self, value):
        if value.empresa_id != self.context["request"].user.empresa_id:
            raise serializers.ValidationError("Planta inválida.")
        return value

    def validate_porta(self, value):
        if not value.isdigit() or not 1 <= int(value) <= 65535:
            raise serializers.ValidationError("Use uma porta entre 1 e 65535.")
        return value

    def validate(self, attrs):
        if self.instance and self.instance.escrita_habilitada:
            mudou_destino = any(
                getattr(self.instance, campo) != attrs[campo]
                for campo in ("ip", "porta", "planta")
                if campo in attrs
            )
            if mudou_destino and attrs.get("escrita_habilitada", True):
                raise serializers.ValidationError({
                    "escrita_habilitada": "Desabilite os comandos antes de alterar o destino do CLP."
                })

        def valor(campo):
            return attrs.get(campo, getattr(self.instance, campo, None))

        if valor("tanque") and valor("ativo"):
            # Um tanque físico só pode ser comandado por uma planta.
            repetido = Clp.objects.filter(
                ip=valor("ip"), porta=valor("porta"), tanque=valor("tanque"), ativo=True
            ).exclude(pk=getattr(self.instance, "pk", None))
            if repetido.exists():
                raise serializers.ValidationError({
                    "tanque": "Este tanque já está vinculado a outro CLP ativo com o mesmo IP e porta."
                })
            outro = Clp.objects.filter(planta=valor("planta"), ativo=True).exclude(
                tanque=""
            ).exclude(pk=getattr(self.instance, "pk", None))
            if outro.exists():
                raise serializers.ValidationError({
                    "tanque": "Esta planta já possui um CLP de produção. Cada planta usa um tanque."
                })
        return attrs


class SensorSerializer(serializers.ModelSerializer):
    unidade_label = serializers.CharField(source="unidade_exibicao", read_only=True)
    tipo_label = serializers.CharField(source="get_tipo_display", read_only=True)
    registro_label = serializers.CharField(source="get_tipo_registro_display", read_only=True)
    clp_nome = serializers.CharField(source="clp.nome", read_only=True)
    clp_endereco = serializers.CharField(source="clp.__str__", read_only=True)
    clp_ativo = serializers.BooleanField(source="clp.ativo", read_only=True)
    pode_escrever = serializers.BooleanField(read_only=True)
    valor_atual = serializers.FloatField(read_only=True, default=None)
    lido_em = serializers.DateTimeField(read_only=True, default=None)
    estado = serializers.SerializerMethodField()

    class Meta:
        model = Sensor
        fields = "__all__"

    def get_estado(self, obj):
        if not obj.clp.ativo:
            return "desativado"
        lido_em = getattr(obj, "lido_em", None)
        if obj.clp.status == "offline":
            return "offline"
        if lido_em is None:
            return "sem_leitura"
        if (timezone.now() - lido_em).total_seconds() > 15:
            return "desatualizado"
        if not obj.minimo <= obj.valor_atual <= obj.maximo:
            return "fora_limite"
        return "online"

    def validate_clp(self, value):
        if value.planta.empresa_id != self.context["request"].user.empresa_id:
            raise serializers.ValidationError("CLP inválido.")
        return value

    def validate(self, attrs):
        low = attrs.get("minimo", getattr(self.instance, "minimo", 0))
        high = attrs.get("maximo", getattr(self.instance, "maximo", 0))
        if not math.isfinite(low) or not math.isfinite(high) or low > high:
            raise serializers.ValidationError("Limites inválidos.")
        if attrs.get("endereco", 0) > 65535:
            raise serializers.ValidationError("Endereço fora da faixa Modbus.")

        tipo = attrs.get("tipo", getattr(self.instance, "tipo", None))
        unidade = attrs.get("unidade", getattr(self.instance, "unidade", None))
        alterou_unidade = not self.instance or (
            tipo != self.instance.tipo or unidade != self.instance.unidade
        )
        if alterou_unidade and unidade not in Sensor.UNIDADES_POR_TIPO.get(tipo, {}):
            raise serializers.ValidationError({"unidade": "Selecione uma unidade compatível com o tipo."})

        registro = attrs.get("tipo_registro", getattr(self.instance, "tipo_registro", None))
        gravavel = attrs.get("gravavel", getattr(self.instance, "gravavel", False))
        if gravavel and registro == Sensor.TipoRegistro.INPUT_STATUS:
            raise serializers.ValidationError({"gravavel": "Entrada discreta é somente leitura."})
        if self.instance and self.instance.gravavel and gravavel:
            mudou_destino = any(
                getattr(self.instance, campo) != attrs[campo]
                for campo in ("clp", "tipo_registro", "endereco")
                if campo in attrs
            )
            if mudou_destino:
                raise serializers.ValidationError({
                    "gravavel": "Desabilite a escrita antes de alterar o endereço ou o registro."
                })
        return attrs
