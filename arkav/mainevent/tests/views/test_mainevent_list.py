from arkav.arkavauth.models import User
from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import MaineventCategory
from arkav.mainevent.serializers import MaineventSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class MaineventListTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1', full_name='a', current_education='SMA')

        category_seminar = MaineventCategory.objects.create(name='Seminar')
        Mainevent.objects.create(name='Advance Seminar', category=category_seminar, education_level='SMA')

    def test_list_mainevents(self):
        '''
        List of mainevents will be returned
        '''
        url = reverse('mainevent-list')
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res_mainevents = res.data
        self.assertEqual(len(res_mainevents), Mainevent.objects.count())
        for res_mainevent in res_mainevents:
            mainevent = Mainevent.objects.get(id=res_mainevent['id'])
            self.assertDictEqual(res_mainevent, MaineventSerializer(mainevent).data)

    def test_list_mainevents_unauthorized(self):
        '''
        If the user hasnt logged in, the result will be 401
        '''
        url = reverse('mainevent-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
