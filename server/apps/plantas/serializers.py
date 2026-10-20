from rest_framework import serializers
from apps.plantas.models import Planta ,Clp , Sensor



class PlantaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model  = Planta
        fields = ['idclp','nome','localizacao','uuid','idplanta']

    

class ClpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Clp
        fields = ['nome','ip','porta','ativo','planta']
        

class SensorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Sensor
        fields = '__all__'
    