# Modelo do uploader do tutorial Django DRF (Image e Document).
import uuid
from django.db import migrations, models
import uploader.models.document
import uploader.models.image

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name='Document', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('attachment_key', models.UUIDField(default=uuid.uuid4, unique=True)),
            ('public_id', models.UUIDField(default=uuid.uuid4, unique=True)),
            ('file', models.FileField(upload_to=uploader.models.document.document_file_path)),
            ('description', models.CharField(blank=True, max_length=255)),
            ('uploaded_on', models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name='Image', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('attachment_key', models.UUIDField(default=uuid.uuid4, unique=True)),
            ('public_id', models.UUIDField(default=uuid.uuid4, unique=True)),
            ('file', models.ImageField(upload_to=uploader.models.image.image_file_path)),
            ('description', models.CharField(blank=True, max_length=255)),
            ('uploaded_on', models.DateTimeField(auto_now_add=True)),
        ]),
    ]
