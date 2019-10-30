from arkav.competition.models import Task
from django.db import migrations
import jsonfield.fields


def forward_func(apps, schema_editor):
    for task in Task.objects.all():
        task.widget_parameters_json = {
            'description': task.widget_parameters
        }
        task.save()


def reverse_func(apps, schema_editor):
    for task in Task.objects.all():
        task.widget_parameters = task.widget_parameters_json['description']
        task.save()


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0003_taskresponse_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='widget_parameters_json',
            field=jsonfield.fields.JSONField(null=True),
        ),
        migrations.RunPython(forward_func, reverse_func),
        migrations.RemoveField(
            model_name='task',
            name='widget_parameters',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='widget_parameters_json',
            new_name='widget_parameters',
        ),
    ]
