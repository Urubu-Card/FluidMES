from rest_framework import serializers
from apps.producao.models import Receita,Pedido

class ReceitaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Receita
        fields= ["*"]


class PedidosSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pedido
        fields = '__all__' 

