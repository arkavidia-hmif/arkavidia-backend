from arkav.arkavauth.models import User
from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import MaineventCategory
from arkav.mainevent.models import Stage
from arkav.mainevent.models import Task
from arkav.mainevent.models import TaskCategory
from arkav.mainevent.models import TaskWidget
from arkav.mainevent.models import Registrant
from arkav.mainevent.models import TaskResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrantDetailTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1', full_name='User 1')
        self.user2 = User.objects.create_user(email='user2', full_name='User 2')
        self.category = MaineventCategory.objects.create(name='Mainevent Category')
        self.mainevent = Mainevent.objects.create(name='Mainevent 1', category=self.category)
        self.stage = Stage.objects.create(mainevent=self.mainevent, name='Stage 1')

        self.task1 = Task.objects.create(
            name='abc',
            stage=self.stage,
            widget=TaskWidget.objects.create(name='widget 1'),
            category=TaskCategory.objects.create(name='category 1'),
            widget_parameters={
                'description': 'Halo, {{ registrant.user.full_name }}!',
                'original': 'Halo, {{ registrant.user.full_name }}!',
            }
        )
        self.task2 = Task.objects.create(
            name='abc',
            stage=self.stage,
            widget=TaskWidget.objects.create(name='widget 2'),
            category=TaskCategory.objects.create(name='category 2'),
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
            mainevent=self.mainevent,
            user=self.user1,
        )

        TaskResponse.objects.create(registrant=self.registrant, task=self.task1, response='abc')

    def test_registrant_detail(self):
        '''
        Detail of a registrant will be returned
        Widget parameters of a task will be rendered as template
        '''
        url = reverse('mainevent-registrant-detail', kwargs={'registrant_id': self.registrant.id})
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data['stages']), 1)
        self.assertEqual(len(res.data['stages'][0]['tasks']), 3)
        self.assertEqual(res.data['stages'][0]['tasks'][0]['widget_parameters']['description'], 'Halo, User 1!')
        self.assertEqual(res.data['stages'][0]['tasks'][0]['widget_parameters']['original'],
                         'Halo, {{ registrant.user.full_name }}!')
        self.assertEqual(res.data['stages'][0]['tasks'][1]['widget_parameters']['description'], 'Tanpa template')
        self.assertEqual(res.data['stages'][0]['tasks'][1]['widget_parameters']['original'], 'Tanpa template')
        self.assertEqual(res.data['stages'][0]['tasks'][2]['widget_parameters']['description'],
                         '601')  # 600 + registrant id
        self.assertEqual(res.data['stages'][0]['tasks'][2]['widget_parameters']['original'], '{{ registrant_number }}')

        self.assertIn('task_responses', res.data)
        self.assertEqual(len(res.data['task_responses']), 1)
        self.assertEqual(res.data['task_responses'][0]['task_id'], self.task1.id)
        self.assertEqual(res.data['task_responses'][0]['response'], 'abc')
