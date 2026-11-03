"""Autenticação Django por e-mail ou username, sem diferenciar maiúsculas."""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username or kwargs.get('email') or kwargs.get('login')
        if not identifier or password is None:
            return None
        User = get_user_model()
        try:
            user = User._default_manager.get(
                Q(email__iexact=identifier.strip()) | Q(username__iexact=identifier.strip())
            )
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            # Equivalente ao backend padrão para não facilitar a enumeração de usuários.
            make_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
