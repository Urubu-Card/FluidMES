from rest_framework import serializers
from apps.plantas.models import Planta ,Clp



class PlantaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model  = Planta
        fields = ['nome','uuid','localizacao']
    

class ClpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Clp
        fields = ['nome','ip','porta','ativo']