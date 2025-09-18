# Generated migration for simple code system

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='simple_code',
            field=models.CharField(blank=True, max_length=4, verbose_name='간단 코드'),
        ),
        migrations.AddField(
            model_name='question',
            name='creator_session',
            field=models.CharField(blank=True, max_length=40, verbose_name='생성자 세션'),
        ),
        migrations.AddField(
            model_name='question',
            name='last_activity',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='마지막 활동'),
        ),
    ]
