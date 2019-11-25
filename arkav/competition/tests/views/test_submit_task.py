from arkav.arkavauth.models import User
from arkav.competition.models import Competition
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from arkav.competition.models import Task
from arkav.competition.models import TaskCategory
from arkav.competition.models import TaskWidget
from arkav.competition.models import UserTaskResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SubmitTeamTaskTestCase(APITestCase):
    def setUp(self):
        self.competition_ctf = Competition.objects.create(name='Capture the Flag', max_team_members=3)
        self.ctf_stage_registration = self.competition_ctf.stages.create(name='CTF Registration', order=1)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')

        self.ctf_team1 = Team.objects.create(name='ctf1', competition=self.competition_ctf, team_leader=self.user1)
        self.ctf_team2 = Team.objects.create(name='ctf2', competition=self.competition_ctf, team_leader=self.user2)

        TeamMember.objects.create(team=self.ctf_team1, user=self.user1)
        TeamMember.objects.create(team=self.ctf_team2, user=self.user2)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.ctf_upload_ktm_task = Task.objects.create(
            name='Upload KTM',
            stage=self.ctf_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )

    def test_submit_team_task(self):
        '''
        Submit a task response
        '''
        url = reverse(
            'competition-team-task-detail',
            kwargs={'team_id': self.ctf_team1.pk, 'task_id': self.ctf_upload_ktm_task.pk})
        self.client.force_authenticate(self.user1)
        data = {
            'response': 'Upload KTM',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_submit_at_others_task(self):
        '''
        Submitting at other task
        '''
        url = reverse(
            'competition-team-task-detail',
            kwargs={'team_id': self.ctf_team1.pk, 'task_id': self.ctf_upload_ktm_task.pk})
        self.client.force_authenticate(self.user2)
        data = {
            'response': 'Upload KTM'
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class SubmitUserTaskTestCase(APITestCase):
    def setUp(self):
        self.competition_ctf = Competition.objects.create(name='Capture the Flag', max_team_members=3)
        self.ctf_stage_registration = self.competition_ctf.stages.create(name='CTF Registration', order=1)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')
        self.user3 = User.objects.create_user(email='user3')

        self.ctf_team = Team.objects.create(name='ctf1', competition=self.competition_ctf, team_leader=self.user1)

        self.team_member1 = TeamMember.objects.create(team=self.ctf_team, user=self.user1)
        self.team_member2 = TeamMember.objects.create(team=self.ctf_team, user=self.user2)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.ctf_upload_ktm_task = Task.objects.create(
            name='Upload KTM',
            stage=self.ctf_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
            is_user_task=True,
        )

    def test_submit_user_task(self):
        '''
        Submit user task
        '''
        url = reverse(
            'competition-team-task-detail',
            kwargs={'team_id': self.ctf_team.pk, 'task_id': self.ctf_upload_ktm_task.pk})
        self.client.force_authenticate(self.user2)
        data = {
            'response': 'Upload KTM',
            'teamMemberId': self.team_member1.pk,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user_task_response = UserTaskResponse.objects.first()
        self.assertEqual(user_task_response.response, data['response'])
        self.assertEqual(user_task_response.team_member.id, data['teamMemberId'])

    def test_submit_user_task_using_user_id(self):
        '''
        Submit user task
        '''
        url = reverse(
            'competition-team-task-detail',
            kwargs={'team_id': self.ctf_team.pk, 'task_id': self.ctf_upload_ktm_task.pk})
        self.client.force_authenticate(self.user2)
        data = {
            'response': 'Upload KTM',
            'userId': self.team_member1.pk,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user_task_response = UserTaskResponse.objects.first()
        self.assertEqual(user_task_response.response, data['response'])
        self.assertEqual(user_task_response.team_member.id, data['userId'])

    def test_submit_user_task_without_user_id(self):
        '''
        Submit user task without user id, it will be treated as current user
        '''
        url = reverse(
            'competition-team-task-detail',
            kwargs={'team_id': self.ctf_team.pk, 'task_id': self.ctf_upload_ktm_task.pk})
        self.client.force_authenticate(self.user2)
        data = {
            'response': 'Upload KTM',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user_task_response = UserTaskResponse.objects.first()
        self.assertEqual(user_task_response.response, data['response'])
        self.assertEqual(user_task_response.team_member.id, self.user2.id)

    def test_submit_user_task_not_team_member(self):
        '''
        If someone submit user task to a team that is not his/hers, the code will be 404
        '''
        url = reverse(
            'competition-team-task-detail',
            kwargs={'team_id': self.ctf_team.pk, 'task_id': self.ctf_upload_ktm_task.pk})
        self.client.force_authenticate(self.user3)
        data = {
            'response': 'Upload KTM',
            'userId': self.team_member1.pk,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
