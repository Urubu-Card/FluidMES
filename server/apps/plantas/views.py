from rest_framework                 import generics
from apps.plantas.models            import Planta ,Clp , Sensor
from apps.plantas.serializers       import PlantaSerializer,ClpSerializer,SensorSerializer
from rest_framework.permissions     import IsAuthenticated



class PlantaListView(generics.ListAPIView):
    serializer_class = PlantaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        usuario = self.request.user
        return Planta.objects.filter(empresa=usuario.empresa)
    
class ClpListView(generics.ListAPIView):
    serializer_class = ClpSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
         user = self.request.user
         return Clp.objects.filter(planta__empresa=user.empresa)
     
class SensoresListView(generics.ListAPIView):
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Sensor.objects.filter(clp__planta__empresa = user.empresa)

#class 