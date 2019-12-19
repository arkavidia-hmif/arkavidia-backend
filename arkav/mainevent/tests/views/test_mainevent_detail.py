from arkav.arkavauth.models import User
from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import MaineventCategory
from arkav.mainevent.serializers import MaineventDetailsSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class MaineventDetailTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1')

        category_seminar = MaineventCategory.objects.create(name='Seminar')
        self.mainevent1 = Mainevent.objects.create(name='Advance Seminar', category=category_seminar)

    def test_detail_mainevent(self):
        '''
        Detail of mainevent will be returned
        '''
        url = reverse('mainevent-detail', kwargs={'mainevent_id': self.mainevent1.id})
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertDictEqual(res.data, MaineventDetailsSerializer(self.mainevent1).data)

    def test_detail_mainevent_unknown(self):
        '''
        Wrong id will return 404
        '''
        url = reverse('mainevent-detail', kwargs={'mainevent_id': 3456})
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_detail_mainevent_unauthorized(self):
        '''
        If the user hasnt logged in, the result will be 401
        '''
        url = reverse('mainevent-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
