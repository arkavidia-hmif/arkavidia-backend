from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import UserSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class LoginTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('yonas@gmail.com', 'password',
                                              full_name='Yonas Adiel',
                                              is_email_confirmed=True)
        self.user2 = User.objects.create_user('nella@gmail.com', 'password')

    def test_login(self):
        url = reverse('auth-login')
        data = {
            'email': 'YONAS@GMAIL.COM',
            'password': 'password',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        self.assertDictEqual(res.data, UserSerializer(self.user1).data)

    def test_login_wrong_password(self):
        url = reverse('auth-login')
        data = {
            'email': 'YONAS@GMAIL.COM',
            'password': 'hahahaha',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(res.data['code'], 'login_failed')

    def test_login_not_confirmed(self):
        '''
        User won't be able to login if the email is not confirmed yet.
        '''
        url = reverse('auth-login')
        data = {
            'email': 'nella@gmail.com',
            'password': 'password',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.assertEqual(res.data['code'], 'account_email_not_confirmed')

    def test_login_already_login(self):
        '''
        User won't be able to login if the user has already login (403)
        '''
        url = reverse('auth-login')
        data = {
            'email': 'YONAS@GMAIL.COM',
            'password': 'password',
        }
        self.client.force_authenticate(self.user1)
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
