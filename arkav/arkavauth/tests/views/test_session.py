from arkav.arkavauth.serializers import UserSerializer
from arkav.arkavauth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SessionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('yonas@gmail.com', 'password',
                                             full_name='Yonas Adiel',
                                             is_email_confirmed=True)

    def test_session(self):
        '''
        Will get user session
        '''
        url = reverse('auth-current-session')
        self.client.force_authenticate(user=self.user)
        res = self.client.get(url, format='json')
        self.assertEqual(res.data, UserSerializer(self.user).data)

    def test_session_unauthorized(self):
        '''
        If the user is not logged in, will get 401
        '''
        url = reverse('auth-current-session')
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
