from rest_framework.viewsets        import ModelViewSet
from apps.plantas.models            import Planta ,Clp , Sensor
from apps.plantas.serializers       import PlantaSerializer,ClpSerializer,SensorSerializer
from rest_framework.permissions     import IsAuthenticated
from rest_framework.exceptions      import NotFound, PermissionDenied


class PlantasView(ModelViewSet):
    queryset = Planta.objects.all()
    serializer_class = PlantaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Planta.objects.filter(empresa=self.request.user.empresa)
    
    def perform_create(self, serializer):
        if self.request.user.role == 3:
            raise PermissionDenied("Funcionarios não podem criar plantas plantas")
        
        serializer.save(empresa=self.request.user.empresa) 
        
        
    
class ClpListView(ModelViewSet):
    serializer_class = ClpSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
         user = self.request.user
         return Clp.objects.filter(planta__empresa=user.empresa)
     
class SensoresListView(ModelViewSet):
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Sensor.objects.filter(clp__planta__empresa = user.empresa)
