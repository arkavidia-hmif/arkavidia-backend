from arkav.arkavauth.models import User
from arkav.preevent.models import Preevent
from arkav.preevent.models import Registrant
from arkav.preevent.serializers import RegistrantSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrantListTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user')

        preevent1 = Preevent.objects.create(name='Preevent 1')
        preevent2 = Preevent.objects.create(name='Preevent 2')

    def test_list_registrants(self):
        '''
        List of registrants will be returned
        '''
        url = reverse('preevent-registrant-list')
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res_registrants = res.data
        print(res.data)
        self.assertEqual(len(res_registrants), Registrant.objects.count())
        for res_registrant in res_registrants:
            registrant = Registrant.objects.get(id=res_registrant['id'])
            self.assertDictEqual(res_registrant, RegistrantSerializer(registrant).data)

    def test_list_registrants_unauthorized(self):
        '''
        If the user isn't logged in, returns 401
        '''
        url = reverse('preevent-registrant-list')
        res = self.client.get(url)
        print(res)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
