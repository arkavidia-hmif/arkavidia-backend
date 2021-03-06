# Generated by Django 2.2.6 on 2019-10-24 11:18

from django.conf import settings
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('announcement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='title',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.RemoveField(
            model_name='announcement',
            name='user',
        ),
        migrations.AddField(
            model_name='announcement',
            name='user',
            field=models.ManyToManyField(related_name='announcements', to=settings.AUTH_USER_MODEL),
        ),
    ]
