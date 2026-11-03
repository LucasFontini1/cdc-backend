from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [('core', '0004_alter_user_email_alter_user_passage_id')]
    operations = [migrations.RemoveField(model_name='user', name='passage_id')]
