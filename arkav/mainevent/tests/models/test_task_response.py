from arkav.arkavauth.models import User
from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import MaineventCategory
from arkav.mainevent.models import Registrant
from arkav.mainevent.models import Task
from arkav.mainevent.models import TaskResponse
from arkav.mainevent.models import TaskCategory
from arkav.mainevent.models import TaskWidget
from django.test import TestCase


class TaskResponseModelTestCase(TestCase):
    def setUp(self):
        self.category_seminar = MaineventCategory.objects.create(name='Seminar')
        self.seminar1 = Mainevent.objects.create(name='Advance Seminar 1', category=self.category_seminar)
        self.seminar1_stage_registration = self.seminar1.stages.create(name='Registration', order=1)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')
        self.user3 = User.objects.create_user(email='user3')
        self.user4 = User.objects.create_user(email='user4')

        self.seminar_registrant1 = Registrant.objects.create(mainevent=self.seminar1, user=self.user1)
        self.seminar_registrant2 = Registrant.objects.create(mainevent=self.seminar1, user=self.user2)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.widget_text = TaskWidget.objects.create(name='Text')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.seminar_upload_ktm_task = Task.objects.create(
            name='Upload KTM',
            stage=self.seminar1_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )
        self.seminar_enter_shirt_sizes = Task.objects.create(
            name='Shirt sizes',
            stage=self.seminar1_stage_registration,
            category=self.category_documents,
            widget=self.widget_text,
        )

    def test_task_response_default_state(self):
        # Create task response for a task that requires validation
        task_response_1 = TaskResponse.objects.create(registrant=self.seminar_registrant1,
                                                      task=self.seminar_upload_ktm_task)
        self.assertEqual(task_response_1.status, TaskResponse.AWAITING_VALIDATION)

        # Create task response for a task that don't require validation
        task_response_2 = TaskResponse.objects.create(registrant=self.seminar_registrant1,
                                                      task=self.seminar_enter_shirt_sizes)
        self.assertEqual(task_response_2.status, TaskResponse.COMPLETED)

    def test_task_response_override_defaults(self):
        # Create task response for a task that requires validation
        # Ensure defaults don't mess with manual status override
        task_response_1 = TaskResponse.objects.create(
            registrant=self.seminar_registrant1, task=self.seminar_upload_ktm_task, status=TaskResponse.COMPLETED)
        self.assertEqual(task_response_1.status, TaskResponse.COMPLETED)

    def test_edit_task_response(self):
        task_response_1 = TaskResponse.objects.create(registrant=self.seminar_registrant1,
                                                      task=self.seminar_upload_ktm_task)
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

        task_response_2 = TaskResponse.objects.create(registrant=self.seminar_registrant2,
                                                      task=self.seminar_enter_shirt_sizes)
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
