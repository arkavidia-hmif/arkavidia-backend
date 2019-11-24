from arkav.arkavauth.models import User
from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import MaineventCategory
from arkav.mainevent.models import Registrant
from arkav.mainevent.models import Task
from arkav.mainevent.models import TaskResponse
from arkav.mainevent.models import TaskCategory
from arkav.mainevent.models import TaskWidget
from django.db import IntegrityError
from django.test import TestCase


class RegistrantModelTestCase(TestCase):
    def setUp(self):
        self.category_seminar = MaineventCategory.objects.create(name='Seminar')
        self.seminar1 = Mainevent.objects.create(name='Advance Seminar 1', category=self.category_seminar)
        self.seminar2 = Mainevent.objects.create(name='Talk Show', category=self.category_seminar)
        self.mainevent_without_stages = Mainevent.objects.create(name='Empty', category=self.category_seminar)

        self.seminar1_stage_final = self.seminar1.stages.create(name='Seminar 1 Final', order=3)
        self.seminar1_stage_qual = self.seminar1.stages.create(name='Seminar 1 Qualification', order=2)
        self.seminar1_stage_registration = self.seminar1.stages.create(name='Seminar 1 Registration', order=1)

        self.seminar2_stage_registration = self.seminar2.stages.create(name='Seminar 2 Registration', order=1)
        self.seminar2_stage_contest = self.seminar2.stages.create(name='Seminar 2 Contest', order=2)
        self.seminar2_empty_stage = self.seminar2.stages.create(name='Seminar 2 Empty', order=99)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')
        self.user3 = User.objects.create_user(email='user3')
        self.user4 = User.objects.create_user(email='user4')
        self.user5 = User.objects.create_user(email='user5')
        self.user6 = User.objects.create_user(email='user6')
        self.user7 = User.objects.create_user(email='user7')
        self.user8 = User.objects.create_user(email='user8')

        self.registrant1 = Registrant.objects.create(mainevent=self.seminar2, user=self.user1)
        self.registrant2 = Registrant.objects.create(mainevent=self.seminar2, user=self.user2)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.category_payment = TaskCategory.objects.create(name='Payment')
        self.widget_text = TaskWidget.objects.create(name='Text')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.seminar2_upload_ktm_task = Task.objects.create(
            name='Upload KTM',
            stage=self.seminar2_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )
        self.seminar2_payment = Task.objects.create(
            name='Upload proof of payment',
            stage=self.seminar2_stage_registration,
            category=self.category_payment,
            widget=self.widget_file,
            requires_validation=True,
        )
        self.seminar2_enter_shirt_sizes = Task.objects.create(
            name='Shirt sizes',
            stage=self.seminar2_stage_registration,
            category=self.category_documents,
            widget=self.widget_text,
        )
        self.seminar2_upload_resume = Task.objects.create(
            name='Upload writeup',
            stage=self.seminar2_stage_contest,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )

    def test_registrant_defaults(self):
        new_registrant = Registrant.objects.create(mainevent=self.seminar1, user=self.user3)
        self.assertEqual(new_registrant.active_stage.name, 'Seminar 1 Registration')

    def test_registrant_override_defaults(self):
        new_registrant = Registrant.objects.create(
            mainevent=self.seminar2,
            active_stage=self.seminar2_stage_contest,
            user=self.user4
        )
        self.assertEqual(new_registrant.active_stage.name, 'Seminar 2 Contest')

    def test_edit_registrant(self):
        '''
        Ensure manual defaults for active_stage does not mess up registrant instance editing.
        '''
        self.assertEqual(self.registrant2.active_stage, self.seminar2_stage_registration)
        self.registrant2.active_stage = self.seminar2_stage_contest
        self.registrant2.save()
        self.assertEqual(self.registrant2.active_stage, self.seminar2_stage_contest)

    def test_create_registrant_without_mainevent(self):
        try:
            Registrant.objects.create(user=self.user8)
            self.fail(msg='Registrant creation should fail if not given a mainevent.')
        except ValueError:
            pass

    def test_create_registrant_with_stageless_mainevent(self):
        try:
            Registrant.objects.create(mainevent=self.mainevent_without_stages, user=self.user5)
            self.fail(msg='Registrant creation should fail if given a mainevent without any stage.')
        except ValueError:
            pass

    def test_enforce_user_can_only_participate_one_event(self):
        new_user = User.objects.create(email='new_user')
        Registrant.objects.create(mainevent=self.seminar1, user=new_user)
        try:
            Registrant.objects.create(mainevent=self.seminar1, user=new_user)
            self.fail('User cannot lead more than one registrant')
        except IntegrityError:
            pass

    def test_task_response_default_state(self):
        # Create task response for a task that requires validation
        task_response_1 = TaskResponse.objects.create(registrant=self.registrant1, task=self.seminar2_upload_ktm_task)
        self.assertEqual(task_response_1.status, TaskResponse.AWAITING_VALIDATION)

        # Create task response for a task that don't require validation
        task_response_2 = TaskResponse.objects.create(registrant=self.registrant1, task=self.seminar2_enter_shirt_sizes)
        self.assertEqual(task_response_2.status, TaskResponse.COMPLETED)

    def test_task_response_override_defaults(self):
        # Create task response for a task that requires validation
        # Ensure defaults don't mess with manual status override
        task_response_1 = TaskResponse.objects.create(
            registrant=self.registrant1, task=self.seminar2_upload_ktm_task, status=TaskResponse.COMPLETED)
        self.assertEqual(task_response_1.status, TaskResponse.COMPLETED)

    def test_edit_task_response(self):
        task_response_1 = TaskResponse.objects.create(registrant=self.registrant1, task=self.seminar2_upload_ktm_task)
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

        task_response_2 = TaskResponse.objects.create(registrant=self.registrant2, task=self.seminar2_enter_shirt_sizes)
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
        self.assertFalse(self.registrant1.has_completed_active_stage)
        self.assertFalse(self.registrant2.has_completed_active_stage)
        self.assertEqual(self.registrant1.visible_stages.count(), 1)
        self.assertEqual(self.registrant2.visible_stages.count(), 1)

        task_response_1 = TaskResponse.objects.create(registrant=self.registrant1, task=self.seminar2_upload_ktm_task)
        task_response_2 = TaskResponse.objects.create(registrant=self.registrant1, task=self.seminar2_payment)
        TaskResponse.objects.create(registrant=self.registrant1, task=self.seminar2_enter_shirt_sizes)
        self.assertFalse(self.registrant1.has_completed_active_stage)

        task_response_1.status = TaskResponse.COMPLETED
        task_response_1.save()
        task_response_2.status = TaskResponse.REJECTED
        task_response_2.save()
        self.assertFalse(self.registrant1.has_completed_active_stage)
        self.assertFalse(self.registrant2.has_completed_active_stage)

        task_response_2.status = TaskResponse.COMPLETED
        task_response_2.save()
        self.assertTrue(self.registrant1.has_completed_active_stage)
        self.assertFalse(self.registrant2.has_completed_active_stage)

        # An stage with no tasks is by definition completed
        self.registrant1.active_stage = self.seminar2_empty_stage
        self.registrant1.save()
        self.assertTrue(self.registrant1.has_completed_active_stage)
        self.assertEqual(self.registrant1.visible_stages.count(), 3)
        self.assertEqual(self.registrant2.visible_stages.count(), 1)

        self.registrant1.active_stage = self.seminar2_stage_contest
        self.registrant1.save()
        self.assertFalse(self.registrant1.has_completed_active_stage)
        self.assertEqual(self.registrant1.visible_stages.count(), 2)
        self.assertEqual(self.registrant2.visible_stages.count(), 1)

        task_response_4 = TaskResponse.objects.create(registrant=self.registrant1, task=self.seminar2_upload_resume)
        task_response_4.status = TaskResponse.COMPLETED
        task_response_4.save()
        self.assertTrue(self.registrant1.has_completed_active_stage)

        # has_completed_active_stage should not core about the completeness of tasks
        # in stages other than the active stage
        task_response_2.status = TaskResponse.REJECTED
        task_response_2.save()
        self.assertTrue(self.registrant1.has_completed_active_stage)
