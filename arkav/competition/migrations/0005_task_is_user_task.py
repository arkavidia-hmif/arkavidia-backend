# Generated by Django 2.2.6 on 2019-10-30 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0004_usertaskresponse'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_user_task',
            field=models.BooleanField(default=False),
        ),
    ]
