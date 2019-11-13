from arkav.arkavauth.models import User
from arkav.preevent.models import Preevent
from arkav.preevent.models import Registrant
from arkav.preevent.models import Task
from arkav.preevent.models import TaskResponse
from arkav.preevent.models import TaskCategory
from arkav.preevent.models import TaskWidget
from django.test import TestCase


class RegistrantModelTestCase(TestCase):
    def setUp(self):
        self.preevent_aa = Preevent.objects.create(name='Arkavidia Academy')
        self.preevent_tcp = Preevent.objects.create(name='Technocamp')
        self.preevent_without_stages = Preevent.objects.create(name='Empty')

        self.aa_stage_registration = self.preevent_aa.stages.create(name='Arkavidia Academy Registration', order=1)
        self.tcp_stage_registration = self.preevent_tcp.stages.create(name='Technocamp Registration', order=1)
        self.tcp_stage_contest = self.preevent_tcp.stages.create(name='Technocamp Contest', order=2)
        self.tcp_empty_stage = self.preevent_tcp.stages.create(name='Technocamp Empty', order=99)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')
        self.user3 = User.objects.create_user(email='user3')

        self.tcp_registrant1 = Registrant.objects.create(user=self.user1, preevent=self.preevent_tcp)
        self.tcp_registrant2 = Registrant.objects.create(user=self.user2, preevent=self.preevent_tcp)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.category_payment = TaskCategory.objects.create(name='Payment')
        self.widget_text = TaskWidget.objects.create(name='Text')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.tcp_upload_ktm_task = Task.objects.create(
            name='Upload KTM',
            stage=self.tcp_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )
        self.tcp_upload_proof_of_payment = Task.objects.create(
            name='Upload proof of payment',
            stage=self.tcp_stage_registration,
            category=self.category_payment,
            widget=self.widget_file,
            requires_validation=True,
        )
        self.tcp_enter_shirt_sizes = Task.objects.create(
            name='Shirt sizes',
            stage=self.tcp_stage_registration,
            category=self.category_documents,
            widget=self.widget_text,
        )
        self.tcp_upload_resume = Task.objects.create(
            name='Upload resume',
            stage=self.tcp_stage_contest,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )

    def test_registrant_defaults(self):
        new_aaregistrant = Registrant.objects.create(user=self.user1, preevent=self.preevent_aa)
        self.assertEqual(new_aaregistrant.active_stage.name, 'Arkavidia Academy Registration')

    def test_registrant_override_defaults(self):
        new_tcpregistrant = Registrant.objects.create(
            user=self.user2,
            preevent=self.preevent_tcp,
            active_stage=self.tcp_stage_contest,
        )
        self.assertEqual(new_tcpregistrant.active_stage.name, 'Technocamp Contest')

    def test_create_registrant_without_preevent(self):
        try:
            Registrant.objects.create(user=self.user2)
            self.fail(msg='Registrant creation should fail if not given a preevent.')
        except ValueError:
            pass

    def test_create_registrant_with_stageless_preevent(self):
        try:
            Registrant.objects.create(user=self.user2, preevent=self.preevent_without_stages)
            self.fail(msg='Registrant creation should fail if given a preevent without any stage.')
        except ValueError:
            pass

    def test_task_response_default_state(self):
        # Create task response for a task that requires validation
        task_response_1 = TaskResponse.objects.create(registrant=self.tcp_registrant1, task=self.tcp_upload_ktm_task)
        self.assertEqual(task_response_1.status, TaskResponse.AWAITING_VALIDATION)

        # Create task response for a task that don't require validation
        task_response_2 = TaskResponse.objects.create(registrant=self.tcp_registrant1, task=self.tcp_enter_shirt_sizes)
        self.assertEqual(task_response_2.status, TaskResponse.COMPLETED)

    def test_task_response_override_defaults(self):
        # Create task response for a task that requires validation
        # Ensure defaults don't mess with manual status override
        task_response_1 = TaskResponse.objects.create(
            registrant=self.tcp_registrant1, task=self.tcp_upload_ktm_task, status=TaskResponse.COMPLETED)
        self.assertEqual(task_response_1.status, TaskResponse.COMPLETED)

    def test_edit_task_response(self):
        task_response_1 = TaskResponse.objects.create(registrant=self.tcp_registrant1, task=self.tcp_upload_ktm_task)
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

        task_response_2 = TaskResponse.objects.create(registrant=self.tcp_registrant2, task=self.tcp_enter_shirt_sizes)
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

    def test_registrant_has_completed_active_stage(self):
        self.assertFalse(self.tcp_registrant1.has_completed_active_stage)
        self.assertFalse(self.tcp_registrant2.has_completed_active_stage)
        self.assertEqual(self.tcp_registrant1.visible_stages.count(), 1)
        self.assertEqual(self.tcp_registrant2.visible_stages.count(), 1)

        task_response_1 = TaskResponse.objects.create(registrant=self.tcp_registrant1, task=self.tcp_upload_ktm_task)
        task_response_2 = TaskResponse.objects.create(registrant=self.tcp_registrant1,
                                                      task=self.tcp_upload_proof_of_payment)
        TaskResponse.objects.create(registrant=self.tcp_registrant1, task=self.tcp_enter_shirt_sizes)
        self.assertFalse(self.tcp_registrant1.has_completed_active_stage)

        task_response_1.status = TaskResponse.COMPLETED
        task_response_1.save()
        task_response_2.status = TaskResponse.REJECTED
        task_response_2.save()
        self.assertFalse(self.tcp_registrant1.has_completed_active_stage)
        self.assertFalse(self.tcp_registrant2.has_completed_active_stage)

        task_response_2.status = TaskResponse.COMPLETED
        task_response_2.save()
        self.assertTrue(self.tcp_registrant1.has_completed_active_stage)
        self.assertFalse(self.tcp_registrant2.has_completed_active_stage)

        # An stage with no tasks is by definition completed
        self.tcp_registrant1.active_stage = self.tcp_empty_stage
        self.tcp_registrant1.save()
        self.assertTrue(self.tcp_registrant1.has_completed_active_stage)
        self.assertEqual(self.tcp_registrant1.visible_stages.count(), 3)
        self.assertEqual(self.tcp_registrant2.visible_stages.count(), 1)

        self.tcp_registrant1.active_stage = self.tcp_stage_contest
        self.tcp_registrant1.save()
        self.assertFalse(self.tcp_registrant1.has_completed_active_stage)
        self.assertEqual(self.tcp_registrant1.visible_stages.count(), 2)
        self.assertEqual(self.tcp_registrant2.visible_stages.count(), 1)

        task_response_4 = TaskResponse.objects.create(registrant=self.tcp_registrant1, task=self.tcp_upload_resume)
        task_response_4.status = TaskResponse.COMPLETED
        task_response_4.save()
        self.assertTrue(self.tcp_registrant1.has_completed_active_stage)

        # has_completed_active_stage should not core about the completeness of tasks
        # in stages other than the active stage
        task_response_2.status = TaskResponse.REJECTED
        task_response_2.save()
        self.assertTrue(self.tcp_registrant1.has_completed_active_stage)
