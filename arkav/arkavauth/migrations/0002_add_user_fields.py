# Generated by Django 2.2.6 on 2019-10-22 08:58

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('arkavauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='birth_date',
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='current_education',
            field=models.CharField(choices=[('SCHOOL', 'SMA / Sederajat'), ('COLLEGE', 'Universitas / Sederajat')],
                                   default=None, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='institution',
            field=models.CharField(blank=True, default=None, max_length=75, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(default=None, max_length=20, null=True),
        ),
    ]
