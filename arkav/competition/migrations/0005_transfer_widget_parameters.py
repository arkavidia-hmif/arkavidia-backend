from arkav.competition.models import Task
from django.db import migrations


def transfer_widget_parameters(apps, schema_editor):
    for task in Task.objects.all():
        task.widget_parameters_json = {
            'description': task.widget_parameters
        }
        task.save()


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0004_task_widget_parameters_json'),
    ]

    operations = [
        migrations.RunPython(transfer_widget_parameters),
    ]
