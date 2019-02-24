# Generated by Django 2.1.5 on 2019-02-24 05:16

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('twitch', '0002_auto_20190223_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='last_verified',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='vip',
            name='current_username',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
        migrations.AlterField(
            model_name='vip',
            name='uuid',
            field=models.CharField(blank=True, default='', help_text='Mojang UUID', max_length=32),
        ),
        migrations.AlterField(
            model_name='whitelist',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='whitelists_joined', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='whitelist',
            name='vips',
            field=models.ManyToManyField(blank=True, related_name='whitelists_joined', to='twitch.VIP'),
        ),
    ]
