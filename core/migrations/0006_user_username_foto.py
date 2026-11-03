from django.core.validators import RegexValidator
from django.db import migrations, models
from django.db.models.functions import Lower
import django.db.models.deletion


def populate_username(apps, schema_editor):
    User = apps.get_model('core', 'User')
    for user in User.objects.filter(username__isnull=True).iterator():
        base = f'user{user.pk}'
        username = base
        n = 1
        while User.objects.filter(username__iexact=username).exists():
            username = f'{base}_{n}'
            n += 1
        user.username = username
        user.save(update_fields=['username'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_remove_user_passage_id'),
        ('uploader', '0001_initial'),
    ]
    operations = [
        migrations.AddField(model_name='user', name='username', field=models.CharField(blank=True, max_length=150, null=True)),
        migrations.AddField(model_name='user', name='foto', field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_foto', to='uploader.image')),
        migrations.RunPython(populate_username, migrations.RunPython.noop),
        migrations.AlterField(model_name='user', name='username', field=models.CharField(max_length=150, unique=True, validators=[RegexValidator(regex='^[a-zA-Z0-9._-]+$', message='Use apenas letras, números, pontos, underscores ou hífens; não use @.')], verbose_name='username')),
        migrations.AlterField(model_name='user', name='name', field=models.CharField(blank=True, help_text='Nome exibido', max_length=255, null=True, verbose_name='name')),
        migrations.AlterField(model_name='user', name='is_active', field=models.BooleanField(default=True, verbose_name='Usuário está ativo')),
        migrations.AlterField(model_name='user', name='is_staff', field=models.BooleanField(default=False, verbose_name='Usuário é da equipe')),
        migrations.AddConstraint(model_name='user', constraint=models.UniqueConstraint(Lower('email'), name='core_user_email_ci_unique')),
        migrations.AddConstraint(model_name='user', constraint=models.UniqueConstraint(Lower('username'), name='core_user_username_ci_unique')),
    ]
