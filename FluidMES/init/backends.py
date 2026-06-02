from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

class MultiLogin(ModelBackend):
    #! OBRIGATÓRIO: Mantenha o nome 'username' no argumento da função!
    def authenticate(self, request, username=None, password=None, **kwargs):
        
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(Q(cpf=username) | Q(email=username))
        except UserModel.DoesNotExist:
            print("NAO EXISTE")
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            print("Retornou o usuario")
            return user
        return None
