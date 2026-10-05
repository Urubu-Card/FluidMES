from rest_framework.viewsets        import ModelViewSet
from apps.producao.models           import Pedido,Receita
#from apps.producao.serializers      import PlantaSerializer,ClpSerializer,SensorSerializer
from rest_framework.permissions     import IsAuthenticated
from rest_framework.exceptions      import NotFound, PermissionDenied


class PedidosView(ModelViewSet):
    ...


class RendimentosView(ModelViewSet):
    ...


class ReceitasView(ModelViewSet):
    ...




# def pedidos(request):
#     return render(request,'pages/pedidos.html',)

# def rendimento(request):
#     return render(request,'pages/rendimentos.html',)

# def receitas(request):
#     return render(request,'pages/receitas.html')