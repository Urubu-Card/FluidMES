from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from validate_docbr import CPF


class MultiLogin(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        UserModel = get_user_model()


        user = UserModel.objects.filter(
            Q(email__iexact=username) | Q(cpf=CPF().mask(username) if username.replace('.', '').replace('-', '').isdigit() else username)
            ).first()

        if user is None:
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None