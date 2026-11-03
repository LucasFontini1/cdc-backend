from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('uploader', '0001_initial'),
        ('core', '0006_user_username_foto'),
    ]
    operations = [
        migrations.AddField(model_name='image', name='owner', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_images', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='document', name='owner', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_documents', to=settings.AUTH_USER_MODEL)),
    ]
