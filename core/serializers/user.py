from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from core.models import User
from uploader.models import Image
from uploader.serializers import ImageSerializer


class UserSerializer(serializers.ModelSerializer):
    foto_attachment_key = serializers.SlugRelatedField(
        source='foto', slug_field='attachment_key', queryset=Image.objects.all(),
        required=False, allow_null=True, write_only=True,
    )
    foto = ImageSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'name', 'foto', 'foto_attachment_key',
            'is_active', 'is_staff', 'is_superuser', 'last_login',
        ]
        read_only_fields = ['id', 'email', 'is_active', 'is_staff', 'is_superuser', 'last_login']

    def validate_username(self, value):
        other = User.objects.filter(username__iexact=value)
        if self.instance:
            other = other.exclude(pk=self.instance.pk)
        if other.exists():
            raise serializers.ValidationError('Este username já está em uso.')
        return value

    def validate_foto_attachment_key(self, value):
        if value is None:
            return None
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError('Faça login para associar uma foto.')
        if value.owner_id != request.user.pk and not request.user.is_staff:
            raise serializers.ValidationError('Esta imagem não pertence ao usuário autenticado.')
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'name', 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Este e-mail já está cadastrado.')
        return value

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('Este username já está em uso.')
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
