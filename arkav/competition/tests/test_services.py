from arkav.announcement.models import Announcement
from arkav.announcement.models import AnnouncementUser
from arkav.arkavauth.models import User
from arkav.competition.models import AbstractTaskResponse
from arkav.competition.models import Competition
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from arkav.competition.models import Task
from arkav.competition.models import TaskCategory
from arkav.competition.models import TaskWidget
from arkav.competition.models import TaskResponse
from arkav.competition.models import UserTaskResponse
from arkav.competition.services import TaskResponseService
from django.test import TestCase


class TaskResponseServiceTestCase(TestCase):
    def setUp(self):
        self.competition_ctf = Competition.objects.create(name='Capture the Flag', max_team_members=3)
        self.ctf_stage_registration = self.competition_ctf.stages.create(name='CTF Registration', order=1)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')
        self.user3 = User.objects.create_user(email='user3')

        self.ctf_team = Team.objects.create(name='ctf1', competition=self.competition_ctf, team_leader=self.user1)

        self.team_member1 = TeamMember.objects.create(team=self.ctf_team, user=self.user1)
        self.team_member2 = TeamMember.objects.create(team=self.ctf_team, user=self.user2)
        self.team_member3 = TeamMember.objects.create(team=self.ctf_team, user=None)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.ctf_team_task = Task.objects.create(
            name='Pembayaran',
            stage=self.ctf_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )

        self.ctf_user_task = Task.objects.create(
            name='Upload KTM',
            stage=self.ctf_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
            is_user_task=True,
        )

    def test_accept_team_task_response(self):
        ctf_team_task_response = TaskResponse(
            task=self.ctf_team_task,
            team=self.ctf_team,
            response=self.ctf_team_task.name,
            status=AbstractTaskResponse.AWAITING_VALIDATION,
        )
        TaskResponseService().accept_task_response(ctf_team_task_response)
        ctf_team_task_response.refresh_from_db()
        self.assertEqual(ctf_team_task_response.status, AbstractTaskResponse.COMPLETED)
        self.assertEqual(AnnouncementUser.objects.count(), 2)
        self.assertEqual('{} Task Completion'.format(ctf_team_task_response.task), Announcement.objects.first().title)

    def test_reject_team_task_response(self):
        ctf_team_task_response = TaskResponse(
            task=self.ctf_team_task,
            team=self.ctf_team,
            response=self.ctf_team_task.name,
            status=AbstractTaskResponse.AWAITING_VALIDATION,
        )
        TaskResponseService().reject_task_response(ctf_team_task_response, "Reason placeholder")
        ctf_team_task_response.refresh_from_db()
        self.assertEqual(ctf_team_task_response.status, AbstractTaskResponse.REJECTED)
        self.assertEqual(AnnouncementUser.objects.count(), 2)
        self.assertEqual('{} Task Rejection'.format(ctf_team_task_response.task), Announcement.objects.first().title)

    def test_accept_user_task_response(self):
        ctf_user_task_response = UserTaskResponse(
            team_member=self.team_member1,
            task=self.ctf_user_task,
            team=self.ctf_team,
            response=self.ctf_team_task.name,
            status=AbstractTaskResponse.AWAITING_VALIDATION,
        )
        TaskResponseService().accept_task_response(ctf_user_task_response)
        ctf_user_task_response.refresh_from_db()
        self.assertEqual(ctf_user_task_response.status, AbstractTaskResponse.COMPLETED)
        self.assertEqual(AnnouncementUser.objects.count(), 1)
        self.assertEqual(AnnouncementUser.objects.first().user, self.user1)
        self.assertEqual('{} Task Completion'.format(ctf_user_task_response.task), Announcement.objects.first().title)

    def test_accept_user_task_response_unregistered_user(self):
        ctf_user_task_response = UserTaskResponse(
            team_member=self.team_member3,
            task=self.ctf_user_task,
            team=self.ctf_team,
            response=self.ctf_team_task.name,
            status=AbstractTaskResponse.AWAITING_VALIDATION,
        )
        TaskResponseService().accept_task_response(ctf_user_task_response)
        ctf_user_task_response.refresh_from_db()
        self.assertEqual(ctf_user_task_response.status, AbstractTaskResponse.COMPLETED)
        self.assertEqual(AnnouncementUser.objects.count(), 0)

    def test_reject_user_task_response(self):
        ctf_user_task_response = UserTaskResponse(
            team_member=self.team_member1,
            task=self.ctf_user_task,
            team=self.ctf_team,
            response=self.ctf_team_task.name,
            status=AbstractTaskResponse.AWAITING_VALIDATION,
        )
        TaskResponseService().reject_task_response(ctf_user_task_response, "Reason placeholder")
        ctf_user_task_response.refresh_from_db()
        self.assertEqual(ctf_user_task_response.status, AbstractTaskResponse.REJECTED)
        self.assertEqual(AnnouncementUser.objects.count(), 1)
        self.assertEqual(AnnouncementUser.objects.first().user, self.user1)
        self.assertEqual('{} Task Rejection'.format(ctf_user_task_response.task), Announcement.objects.first().title)
