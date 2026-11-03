"""Modelo de usuário do template original, ampliado com username e foto."""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from uploader.models import Image

username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9._-]+$',
    message='Use apenas letras, números, pontos, underscores ou hífens; não use @.',
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        if not extra_fields.get('username'):
            raise ValueError('O username é obrigatório.')
        email = self.normalize_email(email).strip().lower()
        extra_fields['username'] = extra_fields['username'].strip()
        user = self.model(email=email, **extra_fields)
        user.full_clean(exclude=['password'])
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields['is_staff'] is not True or extra_fields['is_superuser'] is not True:
            raise ValueError('Superusuário deve ter is_staff=True e is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, verbose_name=_('email'), help_text=_('Email'))
    username = models.CharField(max_length=150, unique=True, validators=[username_validator], verbose_name='username')
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('name'), help_text='Nome exibido')
    foto = models.ForeignKey(
        Image, related_name='user_foto', on_delete=models.SET_NULL,
        null=True, blank=True, default=None,
    )
    is_active = models.BooleanField(default=True, verbose_name='Usuário está ativo')
    is_staff = models.BooleanField(default=False, verbose_name='Usuário é da equipe')

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        constraints = [
            models.UniqueConstraint(Lower('email'), name='core_user_email_ci_unique'),
            models.UniqueConstraint(Lower('username'), name='core_user_username_ci_unique'),
        ]

    def __str__(self):
        return self.username
