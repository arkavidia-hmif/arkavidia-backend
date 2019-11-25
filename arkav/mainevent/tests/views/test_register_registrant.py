from arkav.arkavauth.models import User
from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import MaineventCategory
from arkav.mainevent.models import Stage
from arkav.mainevent.models import Registrant
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegisterRegistrantTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')

        self.category_seminar = MaineventCategory.objects.create(name='Seminar')
        self.mainevent_open = Mainevent.objects.create(name='Open Mainevent', category=self.category_seminar)
        self.mainevent_closed = Mainevent.objects.create(name='Closed Mainevent', is_registration_open=False,
                                                         category=self.category_seminar)
        Stage.objects.create(mainevent=self.mainevent_open, name='Open Mainevent Stage')
        Stage.objects.create(mainevent=self.mainevent_closed, name='Closed Mainevent Stage')

    def test_register_registrant(self):
        '''
        Register to an event
        '''
        url = reverse('mainevent-registrant-register')
        self.client.force_authenticate(self.user1)

        data = {
            'mainevent_id': self.mainevent_open.pk,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Registrant.objects.count(), 1)

        registrant1 = Registrant.objects.first()
        self.assertEqual(registrant1.user, self.user1)
        self.assertEqual(registrant1.mainevent, self.mainevent_open)

    def test_register_registrant_unauthorized(self):
        '''
        If user isn't logged in, returns 401
        '''
        url = reverse('mainevent-registrant-register')

        data = {
            'mainevent_id': self.mainevent_open.pk,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_registrant_already_registered(self):
        '''
        If user is already registered to the mainevent, returns 400
        '''
        url = reverse('mainevent-registrant-register')
        self.client.force_authenticate(self.user1)

        # Creates new registrant to the mainevent
        Registrant.objects.create(mainevent=self.mainevent_open, user=self.user1)

        data = {
            'mainevent_id': self.mainevent_open.pk,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_registrant_registration_closed(self):
        '''
        If the mainevent registration is already closed, returns 400
        '''
        url = reverse('mainevent-registrant-register')
        self.client.force_authenticate(self.user1)

        data = {
            'mainevent_id': self.mainevent_closed.pk,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
