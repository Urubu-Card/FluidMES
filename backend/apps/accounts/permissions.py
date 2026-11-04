from rest_framework.permissions import BasePermission, SAFE_METHODS

class CompanyMember(BasePermission):
    message = 'Conclua o cadastro da sua empresa para utilizar esta área.'

    def has_permission(self, request, view):
        user = request.user
        return bool(user.is_authenticated and user.empresa_id)

class CompanyAccess(CompanyMember):
    """Preposto and Chefe manage their tenant; Funcionário reads."""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        self.message = 'Seu cargo não tem permissão para esta ação.'
        user = request.user
        return user.is_preposto or user.role == user.Role.OPERADOR or request.method in SAFE_METHODS

class OwnerAccess(CompanyMember):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        self.message = 'Esta área é exclusiva do Preposto.'
        return request.user.is_preposto

class RequestCreateAccess(CompanyAccess):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return CompanyMember.has_permission(self, request, view)
        return super().has_permission(request, view)

class EmployeeDirectoryAccess(CompanyMember):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        self.message = 'Somente o Preposto pode administrar funcionários.'
        return request.user.is_preposto or (request.user.role == request.user.Role.OPERADOR and request.method in SAFE_METHODS)
