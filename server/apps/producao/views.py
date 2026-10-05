from rest_framework.viewsets        import ModelViewSet
from apps.producao.models           import Pedido,Receita
from apps.producao.serializers      import PedidosSerializer
from rest_framework.permissions     import IsAuthenticated
from rest_framework.exceptions      import NotFound, PermissionDenied


class PedidosView(ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidosSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Pedido.objects.filter(empresa=self.request.user.empresa)
    
    def perform_create(self, serializer):
        if self.request.user.role == 3:
            raise PermissionDenied("Funcionarios não podem criar Pedidos Pedidos")
        
        serializer.save(empresa=self.request.user.empresa) 
    
    def perform_update(self, serializer):
        if self.request.user.role == 3:
            raise PermissionDenied("Funcionarios não podem editar Pedidos")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        if self.request.user.role == 3:
            raise PermissionDenied("Funcionarios não são permitidos deletar Pedidos")
        
        instance.delete()


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