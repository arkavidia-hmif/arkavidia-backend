from arkav.arkavauth.models import User
from arkav.competition.models import Competition
from arkav.competition.models import Stage
from arkav.competition.models import Task
from arkav.competition.models import TaskCategory
from arkav.competition.models import TaskWidget
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TeamListTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user')
        self.competition = Competition.objects.create(name='Competition 1')
        self.stage = Stage.objects.create(competition=self.competition, name='Stage 1')
        self.task = Task.objects.create(
            name='abc',
            stage=self.stage,
            widget=TaskWidget.objects.create(name='widget 1'),
            category=TaskCategory.objects.create(name='category 1'),
            widget_parameters={
                'description': 'Halo, {{ team.name }}!'
            }
        )
        self.task = Task.objects.create(
            name='abc',
            stage=self.stage,
            widget=TaskWidget.objects.create(name='widget 2'),
            category=TaskCategory.objects.create(name='category 2'),
            widget_parameters={
                'description': 'Tanpa template'
            }
        )
        self.task = Task.objects.create(
            name='abc',
            stage=self.stage,
            widget=TaskWidget.objects.create(name='widget 3'),
            category=TaskCategory.objects.create(name='category 3'),
            widget_parameters={
                'description': '{{ team_number }}'
            }
        )

        self.team = Team.objects.create(
            competition=self.competition,
            name='Team 1',
            institution='Team Institution',
            team_leader=self.user1,
        )

        TeamMember.objects.create(
            team=self.team,
            user=self.user1,
            invitation_full_name=self.user1.full_name,
            invitation_email=self.user1.email,
        )

    def test_team_detail(self):
        '''
        Detail of a team will be returned
        Widget parameters of a task will be rendered as template
        '''
        url = reverse('competition-team-detail', kwargs={'team_id': self.team.id})
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data['stages']), 1)
        self.assertEqual(len(res.data['stages'][0]['tasks']), 3)
        self.assertEqual(res.data['stages'][0]['tasks'][0]['widget_parameters'], 'Halo, Team 1!')
        self.assertEqual(res.data['stages'][0]['tasks'][1]['widget_parameters'], 'Tanpa template')
        self.assertEqual(res.data['stages'][0]['tasks'][2]['widget_parameters'], '101')  # 100 + team id
