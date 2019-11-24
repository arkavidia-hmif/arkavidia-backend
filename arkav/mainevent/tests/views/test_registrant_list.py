from arkav.arkavauth.models import User
from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import MaineventCategory
from arkav.mainevent.models import Stage
from arkav.mainevent.models import Registrant
from arkav.mainevent.serializers import RegistrantSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrantListTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user')

        for i in range(5):
            category = MaineventCategory.objects.create(name='Seminar {}'.format(i))
            mainevent = Mainevent.objects.create(name='Mainevent {}'.format(i), category=category)
            Stage.objects.create(mainevent=mainevent, name='Stage {}'.format(i))
            Registrant.objects.create(
                mainevent=mainevent,
                user=self.user1
            )

    def test_list_registrants(self):
        '''
        List of registrants will be returned
        '''
        url = reverse('mainevent-registrant-list')
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res_registrants = res.data
        self.assertEqual(len(res_registrants), Registrant.objects.count())
        for res_registrant in res_registrants:
            registrant = Registrant.objects.get(id=res_registrant['id'])
            self.assertDictEqual(res_registrant, RegistrantSerializer(registrant).data)

    def test_list_registrants_unauthorized(self):
        '''
        If the user isn't logged in, returns 401
        '''
        url = reverse('mainevent-registrant-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
