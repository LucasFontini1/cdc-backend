"""JWT com entrada única 'login' (e-mail ou username)."""
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, TokenVerifySerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


class EmailOrUsernameTokenSerializer(TokenObtainPairSerializer):
    username_field = 'login'
    # Aceita o campo unificado e preserva compatibilidade com clientes que enviam 'email'.
    login = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A classe-pai marca username_field como obrigatório após get_fields().
        # Os clientes antigos podem informar somente email ou username.
        self.fields['login'].required = False

    def validate(self, attrs):
        identifiers = [attrs[field] for field in ('login', 'email', 'username') if attrs.get(field)]
        if len(identifiers) != 1:
            raise serializers.ValidationError({'login': 'Informe um único campo: login, email ou username.'})
        self.user = authenticate(
            request=self.context.get('request'),
            username=identifiers[0], password=attrs['password'],
        )
        if not self.user:
            raise AuthenticationFailed(_('Credenciais inválidas ou conta inativa.'))
        refresh = self.get_token(self.user)
        return {'refresh': str(refresh), 'access': str(refresh.access_token)}


@extend_schema_view(post=extend_schema(
    summary='Login por e-mail ou username',
    description='Envie {"login":"email-ou-username","password":"..."}. Campos legados email/username também são aceitos.',
    request=EmailOrUsernameTokenSerializer,
))
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailOrUsernameTokenSerializer


@extend_schema_view(post=extend_schema(summary='Renovar JWT', request=TokenRefreshSerializer))
class CustomTokenRefreshView(TokenRefreshView):
    pass


@extend_schema_view(post=extend_schema(summary='Verificar JWT', request=TokenVerifySerializer))
class CustomTokenVerifyView(TokenVerifyView):
    pass
