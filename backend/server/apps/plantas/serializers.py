from rest_framework import serializers
from apps.plantas.models import Planta ,Clp , Sensor



class PlantaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model  = Planta
        fields = ['nome','localizacao','uuid','idplanta']

    

class ClpSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Clp
        fields = ['idclp','nome','ip','porta','ativo','planta']
        
    def validate_planta(self,planta):
        request = self.context['request']
        if planta.empresa_id != request.user.empresa_id:
            raise serializers.ValidationError("Planta não pertence à sua empresa.")
        else: 
            return planta
        

class SensorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Sensor
        fields = '__all__'
    
    def validate_clp(self, clp):
        if clp.planta.empresa_id != self.context['request'].user.empresa_id :
            raise serializers.ValidationError("Clp não pertence à sua empresa.")
        return clp