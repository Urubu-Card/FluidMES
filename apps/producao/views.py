from rest_framework.viewsets        import ModelViewSet
from apps.producao.models           import Pedido,Receita
from apps.producao.serializers      import PedidosSerializer
from rest_framework.permissions     import IsAuthenticated
from rest_framework.exceptions      import NotFound, PermissionDenied
from apps.accounts.permissions      import PodeEscrever


class PedidosView(ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidosSerializer
    permission_classes = [IsAuthenticated,PodeEscrever]
    
    def get_permissions(self):
        if self.action == 'create':
            IsAuthenticated
        else:
            IsAuthenticated and PodeEscrever
    
    def get_queryset(self):
        return Pedido.objects.filter(empresa=self.request.user.empresa)
    
    def perform_create(self, serializer):
        serializer.save(empresa=self.request.user.empresa) 



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