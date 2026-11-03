from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models


def document_file_path(instance, filename):
    return f'documents/{instance.public_id}{Path(filename).suffix.lower()}'


class Document(models.Model):
    attachment_key = models.UUIDField(default=uuid4, unique=True)
    public_id = models.UUIDField(default=uuid4, unique=True)
    file = models.FileField(upload_to=document_file_path)
    description = models.CharField(max_length=255, blank=True)
    uploaded_on = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        related_name='uploaded_documents',
    )

    def __str__(self):
        return f'{self.description} — {self.attachment_key}'

    @property
    def url(self):
        return self.file.url
