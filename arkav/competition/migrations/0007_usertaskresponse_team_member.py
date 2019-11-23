# Generated by Django 2.2.6 on 2019-11-05 10:42

from django.db import migrations, models
import django.db.models.deletion


def move_user_to_team_member_forward(apps, schema_editor):
    UserTaskResponse = apps.get_model('competition', 'UserTaskResponse')
    TeamMember = apps.get_model('competition', 'TeamMember')
    for user_task_response in UserTaskResponse.objects.all():
        team_member = TeamMember.objects.filter(user=user_task_response.user, team=user_task_response.team).first()
        if team_member is None:
            raise Exception('{}, {}'.format(user_task_response.user, user_task_response.team))
        user_task_response.team_member = team_member
        user_task_response.save()


def move_user_to_team_member_reverse(apps, schema_editor):
    UserTaskResponse = apps.get_model('competition', 'UserTaskResponse')
    for user_task_response in UserTaskResponse.objects.all():
        user_task_response.user = user_task_response.team_member.user
        user_task_response.save()


class Migration(migrations.Migration):

    dependencies = [
        ('competition', '0006_merge_migrations'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertaskresponse',
            name='team_member',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='user_task_responses', to='competition.TeamMember'),
        ),
        migrations.RunPython(move_user_to_team_member_forward, move_user_to_team_member_reverse),
        migrations.AlterUniqueTogether(
            name='usertaskresponse',
            unique_together={('task', 'team', 'team_member')},
        ),
        migrations.RemoveField(
            model_name='usertaskresponse',
            name='user',
        ),
    ]