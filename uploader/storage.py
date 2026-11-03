"""Seleciona storage de vídeo local ou Cloudinary conforme as configurações."""
from django.core.files.storage import storages


def video_storage():
    return storages['videos']
