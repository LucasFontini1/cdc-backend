"""Provisiona grupo de mídia e permissões quando as migrações terminam."""
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from uploader.models import Document, Image, Video

MEDIA_GROUP_NAME = 'Uploaders de Mídia'


@receiver(post_migrate)
def ensure_media_group(sender, using, **kwargs):
    if sender.label != 'uploader':
        return
    group, _ = Group.objects.db_manager(using).get_or_create(name=MEDIA_GROUP_NAME)
    permissions = []
    for model in (Image, Document, Video):
        content_type = ContentType.objects.db_manager(using).get_for_model(model)
        for action in ('add', 'view'):
            permission = Permission.objects.db_manager(using).get(
                content_type=content_type, codename=f'{action}_{model._meta.model_name}'
            )
            permissions.append(permission)
    group.permissions.add(*permissions)
