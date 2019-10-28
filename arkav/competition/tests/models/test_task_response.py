from arkav.arkavauth.models import User
from arkav.competition.models import Competition
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from arkav.competition.models import Task
from arkav.competition.models import TaskResponse
from arkav.competition.models import TaskCategory
from arkav.competition.models import TaskWidget
from django.test import TestCase


class TaskResponseModelTestCase(TestCase):
    def setUp(self):
        self.competition_ctf = Competition.objects.create(name='Capture the Flag', max_team_members=3)
        self.ctf_stage_registration = self.competition_ctf.stages.create(name='CTF Registration', order=1)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')
        self.user3 = User.objects.create_user(email='user3')
        self.user4 = User.objects.create_user(email='user4')

        self.ctf_team1 = Team.objects.create(name='ctf1', competition=self.competition_ctf, team_leader=self.user1)
        TeamMember.objects.create(team=self.ctf_team1, user=self.user2)
        TeamMember.objects.create(team=self.ctf_team1, user=self.user3)
        TeamMember.objects.create(team=self.ctf_team1, user=self.user1)

        self.ctf_team2 = Team.objects.create(name='ctf2', competition=self.competition_ctf, team_leader=self.user2)
        TeamMember.objects.create(team=self.ctf_team2, user=self.user1)
        TeamMember.objects.create(team=self.ctf_team2, user=self.user2)
        TeamMember.objects.create(team=self.ctf_team2, user=self.user4)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.widget_text = TaskWidget.objects.create(name='Text')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.ctf_upload_ktm_task = Task.objects.create(
            name='Upload KTM',
            stage=self.ctf_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )
        self.ctf_enter_shirt_sizes = Task.objects.create(
            name='Shirt sizes',
            stage=self.ctf_stage_registration,
            category=self.category_documents,
            widget=self.widget_text,
        )

    def test_task_response_default_state(self):
        # Create task response for a task that requires validation
        task_response_1 = TaskResponse.objects.create(team=self.ctf_team1, task=self.ctf_upload_ktm_task)
        self.assertEqual(task_response_1.status, TaskResponse.AWAITING_VALIDATION)

        # Create task response for a task that don't require validation
        task_response_2 = TaskResponse.objects.create(team=self.ctf_team1, task=self.ctf_enter_shirt_sizes)
        self.assertEqual(task_response_2.status, TaskResponse.COMPLETED)

    def test_task_response_override_defaults(self):
        # Create task response for a task that requires validation
        # Ensure defaults don't mess with manual status override
        task_response_1 = TaskResponse.objects.create(
            team=self.ctf_team1, task=self.ctf_upload_ktm_task, status=TaskResponse.COMPLETED)
        self.assertEqual(task_response_1.status, TaskResponse.COMPLETED)

    def test_edit_task_response(self):
        task_response_1 = TaskResponse.objects.create(team=self.ctf_team1, task=self.ctf_upload_ktm_task)
        self.assertEqual(task_response_1.status, TaskResponse.AWAITING_VALIDATION)

        # Note: status changes are to be handled at the view level
        # The TaskResponse model is only responsible for assigning default statuses
        task_response_1.response = 'testresponse1'
        task_response_1.save()
        self.assertEqual(task_response_1.response, 'testresponse1')
        self.assertEqual(task_response_1.status, TaskResponse.AWAITING_VALIDATION)

        task_response_1.status = TaskResponse.COMPLETED
        task_response_1.save()
        self.assertEqual(task_response_1.response, 'testresponse1')
        self.assertEqual(task_response_1.status, TaskResponse.COMPLETED)

        task_response_1.status = TaskResponse.AWAITING_VALIDATION
        task_response_1.save()
        self.assertEqual(task_response_1.response, 'testresponse1')
        self.assertEqual(task_response_1.status, TaskResponse.AWAITING_VALIDATION)

        task_response_1.status = TaskResponse.REJECTED
        task_response_1.save()
        self.assertEqual(task_response_1.response, 'testresponse1')
        self.assertEqual(task_response_1.status, TaskResponse.REJECTED)

        task_response_2 = TaskResponse.objects.create(team=self.ctf_team2, task=self.ctf_enter_shirt_sizes)
        self.assertEqual(task_response_2.status, TaskResponse.COMPLETED)

        # Note: status changes are to be handled at the view level
        # The TaskResponse model is only responsible for assigning default statuses
        task_response_2.response = 'testresponse2'
        task_response_2.save()
        self.assertEqual(task_response_2.response, 'testresponse2')
        self.assertEqual(task_response_2.status, TaskResponse.COMPLETED)

        task_response_2.status = TaskResponse.REJECTED
        task_response_2.save()
        self.assertEqual(task_response_2.response, 'testresponse2')
        self.assertEqual(task_response_2.status, TaskResponse.REJECTED)
