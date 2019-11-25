from arkav.arkavauth.models import User
from arkav.preevent.models import Preevent
from arkav.preevent.models import Registrant
from arkav.preevent.models import Task
from arkav.preevent.models import TaskResponse
from arkav.preevent.models import TaskCategory
from arkav.preevent.models import TaskWidget
from django.test import TestCase


class TaskResponseModelTestCase(TestCase):
    def setUp(self):
        self.preevent_aa = Preevent.objects.create(name='Arkavidia Academy')
        self.aa_stage_registration = self.preevent_aa.stages.create(name='Arkavidia Academy Registration', order=1)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')
        self.user3 = User.objects.create_user(email='user3')

        self.aa_registrant1 = Registrant.objects.create(user=self.user1, preevent=self.preevent_aa)
        self.aa_registrant2 = Registrant.objects.create(user=self.user2, preevent=self.preevent_aa)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.widget_text = TaskWidget.objects.create(name='Text')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.aa_upload_ktm_task = Task.objects.create(
            name='Upload KTM',
            stage=self.aa_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )
        self.aa_enter_shirt_sizes = Task.objects.create(
            name='Shirt sizes',
            stage=self.aa_stage_registration,
            category=self.category_documents,
            widget=self.widget_text,
        )

    def test_task_response_default_state(self):
        # Create task response for a task that requires validation
        task_response_1 = TaskResponse.objects.create(registrant=self.aa_registrant1, task=self.aa_upload_ktm_task)
        self.assertEqual(task_response_1.status, TaskResponse.AWAITING_VALIDATION)

        # Create task response for a task that don't require validation
        task_response_2 = TaskResponse.objects.create(registrant=self.aa_registrant1, task=self.aa_enter_shirt_sizes)
        self.assertEqual(task_response_2.status, TaskResponse.COMPLETED)

    def test_task_response_override_defaults(self):
        # Create task response for a task that requires validation
        # Ensure defaults don't mess with manual status override
        task_response_1 = TaskResponse.objects.create(
            registrant=self.aa_registrant1, task=self.aa_upload_ktm_task, status=TaskResponse.COMPLETED)
        self.assertEqual(task_response_1.status, TaskResponse.COMPLETED)

    def test_edit_task_response(self):
        task_response_1 = TaskResponse.objects.create(registrant=self.aa_registrant1, task=self.aa_upload_ktm_task)
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

        task_response_2 = TaskResponse.objects.create(registrant=self.aa_registrant2, task=self.aa_enter_shirt_sizes)
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
