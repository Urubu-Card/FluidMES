from rest_framework.permissions import BasePermission, SAFE_METHODS


class PodeEscrever(BasePermission):
    
    message = "Funcionários não têm permissão para alterar este recurso."
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        elif request.method in SAFE_METHODS:
            return True
        else:
            return True if request.user.role != 3 else False