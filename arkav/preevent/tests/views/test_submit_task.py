from arkav.arkavauth.models import User
from arkav.preevent.models import Preevent
from arkav.preevent.models import Registrant
from arkav.preevent.models import Task
from arkav.preevent.models import TaskCategory
from arkav.preevent.models import TaskWidget
from arkav.preevent.models import TaskResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SubmitTaskTestCase(APITestCase):
    def setUp(self):
        self.preevent_aa = Preevent.objects.create(name='Arkavidia Academy')
        self.aa_stage_registration = self.preevent_aa.stages.create(name='Arkavidia Academy Registration', order=1)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')
        self.user3 = User.objects.create_user(email='user3')

        self.aa_registrant = Registrant.objects.create(user=self.user1, preevent=self.preevent_aa)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.aa_upload_ktm_task = Task.objects.create(
            name='Upload KTM',
            stage=self.aa_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )

    def test_submit_user_task(self):
        '''
        Submit user task
        '''
        url = reverse(
            'preevent-registrant-task-detail',
            kwargs={'registrant_id': self.aa_registrant.pk, 'task_id': self.aa_upload_ktm_task.pk})
        self.client.force_authenticate(self.user2)
        data = {
            'response': 'Upload KTM',
            'registrant_id': self.registrant.pk,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        task_response = TaskResponse.objects.first()
        self.assertEqual(task_response.response, data['response'])
        self.assertEqual(task_response.registrant.id, data['registrant_id'])

    def test_submit_user_task_using_user_id(self):
        '''
        Submit user task
        '''
        url = reverse(
            'preevent-registrant-task-detail',
            kwargs={'registrant_id': self.aa_registrant.pk, 'task_id': self.aa_upload_ktm_task.pk})
        self.client.force_authenticate(self.user2)
        data = {
            'response': 'Upload KTM',
            'user_id': self.registrant.user.pk,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        task_response = TaskResponse.objects.first()
        self.assertEqual(task_response.response, data['response'])
        self.assertEqual(task_response.registrant.user.id, data['user_id'])

    def test_submit_user_task_without_user_id(self):
        '''
        Submit user task without user id, it will be treated as current user
        '''
        url = reverse(
            'preevent-registrant-task-detail',
            kwargs={'registrant_id': self.aa_registrant.pk, 'task_id': self.aa_upload_ktm_task.pk})
        self.client.force_authenticate(self.user2)
        data = {
            'response': 'Upload KTM',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        task_response = TaskResponse.objects.first()
        self.assertEqual(task_response.response, data['response'])
        self.assertEqual(task_response.registrant.user.id, self.user2.id)

    def test_submit_user_task_not_registrant_member(self):
        '''
        If someone submit user task to a registrant that is not his/hers, the code will be 404
        '''
        url = reverse(
            'preevent-registrant-task-detail',
            kwargs={'registrant_id': self.aa_registrant.pk, 'task_id': self.aa_upload_ktm_task.pk})
        self.client.force_authenticate(self.user3)
        data = {
            'response': 'Upload KTM',
            'user_id': self.registrant.user.pk,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
