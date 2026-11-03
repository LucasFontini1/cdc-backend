from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('id',)
    list_display = ('email', 'username', 'name', 'is_staff')
    search_fields = ('email', 'username', 'name')
    readonly_fields = ('last_login',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username', 'name', 'foto')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': (
        'email', 'username', 'password1', 'password2', 'name', 'is_active', 'is_staff', 'is_superuser',
    )}),)
