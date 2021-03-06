# Generated by Django 2.2.6 on 2019-10-29 20:51

from django.conf import settings
from django.db import migrations
from django.db import models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('competition', '0003_taskresponse_reason'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTaskResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.TextField()),
                ('reason', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('awaiting_validation', 'Awaiting validation'),
                                                     ('completed', 'Completed'),
                                                     ('rejected', 'Rejected')], max_length=20)),
                ('last_submitted_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                           related_name='user_task_responses', to='competition.Task')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='user_task_responses', to='competition.Team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='user_task_responses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'created_at',
                'unique_together': {('task', 'team', 'user')},
            },
        ),
    ]
