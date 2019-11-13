from arkav.arkavauth.models import User
from arkav.preevent.models import Preevent
from arkav.preevent.models import Stage
from arkav.preevent.models import Task
from arkav.preevent.models import TaskCategory
from arkav.preevent.models import TaskWidget
from arkav.preevent.models import Registrant
from arkav.preevent.models import TaskResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrantListTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')
        self.preevent = Preevent.objects.create(name='Preevent 1')
        self.stage = Stage.objects.create(preevent=self.preevent, name='Stage 1')

        self.task1 = Task.objects.create(
            name='abc',
            stage=self.stage,
            widget=TaskWidget.objects.create(name='widget 1'),
            category=TaskCategory.objects.create(name='category 1'),
            widget_parameters={
                'description': 'Halo, {{ registrant.name }}!',
                'original': 'Halo, {{ registrant.name }}!',
            }
        )
        self.task2 = Task.objects.create(
            name='abc',
            stage=self.stage,
            widget=TaskWidget.objects.create(name='widget 2'),
            category=TaskCategory.objects.create(name='category 2'),
            is_user_task=True,
            widget_parameters={
                'description': 'Tanpa template',
                'original': 'Tanpa template',
            }
        )
        self.task3 = Task.objects.create(
            name='abc',
            stage=self.stage,
            widget=TaskWidget.objects.create(name='widget 3'),
            category=TaskCategory.objects.create(name='category 3'),
            widget_parameters={
                'description': '{{ registrant_number }}',
                'original': '{{ registrant_number }}',
            }
        )

        self.registrant = Registrant.objects.create(
            preevent=self.preevent,
            user=self.user1
        )

        TaskResponse.objects.create(registrant=self.registrant, task=self.task1, response='abc')

    def test_registrant_detail(self):
        '''
        Detail of a registrant will be returned
        Widget parameters of a task will be rendered as template
        '''
        url = reverse('preevent-registrant-detail', kwargs={'registrant_id': self.registrant.id})
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data['stages']), 1)
        self.assertEqual(len(res.data['stages'][0]['tasks']), 3)
        self.assertEqual(res.data['stages'][0]['tasks'][0]['widget_parameters']['description'], 'Halo, Registrant 1!')
        self.assertEqual(res.data['stages'][0]['tasks'][0]['widget_parameters']['original'],
                         'Halo, {{ registrant.name }}!')
        self.assertEqual(res.data['stages'][0]['tasks'][1]['widget_parameters']['description'], 'Tanpa template')
        self.assertEqual(res.data['stages'][0]['tasks'][1]['widget_parameters']['original'], 'Tanpa template')
        self.assertEqual(res.data['stages'][0]['tasks'][2]['widget_parameters']['description'], '101')
        self.assertEqual(res.data['stages'][0]['tasks'][2]['widget_parameters']['original'], '{{ registrant_number }}')

        self.assertIn('task_responses', res.data)
        self.assertEqual(len(res.data['task_responses']), 1)
        self.assertEqual(res.data['task_responses'][0]['task_id'], self.task1.id)
