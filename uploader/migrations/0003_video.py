from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uploader.models.video
import uploader.storage
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ('uploader', '0002_owner'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_key', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('public_id', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('file', models.FileField(storage=uploader.storage.video_storage, upload_to=uploader.models.video.video_file_path)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_videos', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
