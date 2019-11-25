from arkav.arkavauth.models import User
from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import MaineventCategory
from arkav.mainevent.models import Registrant
from arkav.mainevent.models import Task
from arkav.mainevent.models import TaskCategory
from arkav.mainevent.models import TaskWidget
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SubmitRegistrantTaskTestCase(APITestCase):
    def setUp(self):
        category_seminar = MaineventCategory.objects.create(name='Seminar')
        self.seminar1 = Mainevent.objects.create(name='Advance Seminar 1', category=category_seminar)
        self.seminar1_stage_registration = self.seminar1.stages.create(name='Seminar Registration', order=1)

        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')

        self.seminar_registrant1 = Registrant.objects.create(mainevent=self.seminar1, user=self.user1)
        self.seminar_registrant2 = Registrant.objects.create(mainevent=self.seminar1, user=self.user2)

        self.category_documents = TaskCategory.objects.create(name='Documents')
        self.widget_file = TaskWidget.objects.create(name='File')

        self.seminar1_upload_resume_task = Task.objects.create(
            name='Upload Resume',
            stage=self.seminar1_stage_registration,
            category=self.category_documents,
            widget=self.widget_file,
            requires_validation=True,
        )

    def test_submit_registrant_task(self):
        '''
        Submit a task response
        '''
        url = reverse(
            'mainevent-registrant-task-detail',
            kwargs={'registrant_id': self.seminar_registrant1.pk, 'task_id': self.seminar1_upload_resume_task.pk})
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
            'mainevent-registrant-task-detail',
            kwargs={'registrant_id': self.seminar_registrant1.pk, 'task_id': self.seminar1_upload_resume_task.pk})
        self.client.force_authenticate(self.user2)
        data = {
            'response': 'Upload KTM'
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
