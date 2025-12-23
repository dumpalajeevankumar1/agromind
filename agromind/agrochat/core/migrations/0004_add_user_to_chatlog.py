from django.db import migrations, models
from django.conf import settings

def set_default_user(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    ChatLog = apps.get_model('core', 'ChatLog')
    default_user = User.objects.first()
    for log in ChatLog.objects.all():
        log.user = default_user
        log.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_farmerprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatlog',
            name='user',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                null=True,  # temporarily allow null
                on_delete=models.CASCADE,
                related_name='chat_logs'
            ),
        ),
        migrations.RunPython(set_default_user),
        migrations.AlterField(
            model_name='chatlog',
            name='user',
            field=models.ForeignKey(
                to=settings.AUTH_USER_MODEL,
                null=False,  # now make it required
                on_delete=models.CASCADE,
                related_name='chat_logs'
            ),
        ),
    ]
