"""Permissões de modelo do Django: exige view/add/change/delete também no uploader."""
from rest_framework.permissions import DjangoModelPermissions


class MediaModelPermissions(DjangoModelPermissions):
    """Usa permissões do usuário e de seus grupos, com GET protegido."""

    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
