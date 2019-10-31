from django.db import migrations
import jsonfield.fields


def move_widget_parameters_to_json_forward(apps, schema_editor):
    Task = apps.get_model('competition', 'Task')
    for task in Task.objects.all():
        task.widget_parameters_json = {
            'description': task.widget_parameters
        }
        task.save()


def move_widget_parameters_to_json_reverse(apps, schema_editor):
    Task = apps.get_model('competition', 'Task')
    for task in Task.objects.all():
        task.widget_parameters = task.widget_parameters_json.get('description', '')
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
        migrations.RunPython(move_widget_parameters_to_json_forward, move_widget_parameters_to_json_reverse),
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
