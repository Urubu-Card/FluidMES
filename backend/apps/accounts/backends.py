from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class MultiLogin(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        UserModel = get_user_model()


        user = UserModel.objects.filter(
            Q(email__iexact=username) | Q(cpf=username)
            ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None