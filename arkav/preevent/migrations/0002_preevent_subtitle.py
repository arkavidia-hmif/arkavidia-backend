# Generated by Django 2.2.6 on 2019-11-24 03:48

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('preevent', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='preevent',
            name='subtitle',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]