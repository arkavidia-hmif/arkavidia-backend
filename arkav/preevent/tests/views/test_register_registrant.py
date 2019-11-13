from arkav.arkavauth.models import User
from arkav.preevent.models import Preevent
from arkav.preevent.models import Stage
from arkav.preevent.models import Registrant
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegisterRegistrantTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1')
        self.user2 = User.objects.create_user(email='user2')

        self.preevent_open = Preevent.objects.create(name='Open Preevent')
        self.preevent_closed = Preevent.objects.create(name='Closed Preevent', is_registration_open=False)
        Stage.objects.create(preevent=self.preevent_open, name='Open Preevent Stage')
        Stage.objects.create(preevent=self.preevent_closed, name='Closed Preevent Stage')

    def test_register_registrant(self):
        '''
        Creates a registrant objects by registering
        '''
        url = reverse('preevent-registrant-register')
        self.client.force_authenticate(self.user1)

        data = {
            'preevent_id': self.preevent_open.pk,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Registrant.objects.count(), 1)

        registrant1 = Registrant.objects.first()
        self.assertEqual(registrant1.user.email, self.user1.email)

    def test_register_registrant_unauthorized(self):
        '''
        If user isn't logged in, returns 401
        '''
        url = reverse('preevent-registrant-register')

        data = {
            'preevent_id': self.preevent_open.pk,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_registrant_already_registered(self):
        '''
        If user is already registered to the preevent, returns 400
        '''
        url = reverse('preevent-registrant-register')
        self.client.force_authenticate(self.user1)

        # Creates new registrant to the preevent
        new_registrant = Registrant.objects.create(
            preevent=self.preevent_open,
            user=self.user1,
        )

        data = {
            'preevent_id': self.preevent_open.pk,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_registrant_registration_closed(self):
        '''
        If the preevent registration is already closed, returns 400
        '''
        url = reverse('preevent-registrant-register')
        self.client.force_authenticate(self.user1)

        data = {
            'preevent_id': self.preevent_closed.pk,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
