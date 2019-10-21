from arkav.arkavauth.constants import K_INVALID_TOKEN
from arkav.arkavauth.constants import K_REGISTRATION_SUCCESSFUL
from arkav.arkavauth.constants import K_REGISTRATION_CONFIRMATION_SUCCESSFUL
from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import UserSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationTestCase(APITestCase):
    def setUp(self):
        pass

    def test_registration(self):
        '''
        New user will be created with the email, password, and full_name
        Even if other field is present (is_staff, etc), it wont be used
        Email confirmation will be send
        '''
        url = reverse('auth-register')
        data = {
            'fullName': 'Yonas Adiel',
            'email': 'yonazadielwiguna@gmail.com',
            'password': 'password',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user = User.objects.filter(email=data['email']).first()
        self.assertIsNotNone(user)
        self.assertEqual(res.data['code'], K_REGISTRATION_SUCCESSFUL)

    def test_registration_used_email(self):
        '''
        If the email is already used, the response will be 400
        '''
        User.objects.create_user('yonazadielwiguna@gmail.com', 'abcd')
        url = reverse('auth-register')
        data = {
            'fullName': 'Yonas Adiel',
            'email': 'yonazadielwiguna@gmail.com',
            'password': 'password',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_already_login(self):
        '''
        If the user already login, it cant register
        '''
        user = User.objects.create_user('yonas@gmail.com')
        url = reverse('auth-register')
        data = {
            'fullName': 'Yonas Adiel',
            'email': 'yonazadielwiguna@gmail.com',
            'password': 'password',
        }
        self.client.force_authenticate(user)
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class RegistrationConfirmationTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('yonas@gmail.com', is_email_confirmed=False)

    def test_registration_confirmation(self):
        '''
        User account will be confirmed
        '''
        self.assertFalse(self.user1.is_email_confirmed)

        url = reverse('auth-register-confirmation')
        data = {
            'token': self.user1.confirmation_token,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['code'], K_REGISTRATION_CONFIRMATION_SUCCESSFUL)

        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_email_confirmed)

    def test_registration_confirmation_wrong_token(self):
        '''
        User will get error message if the token is wrong
        '''
        url = reverse('auth-register-confirmation')
        data = {
            'token': self.user1.confirmation_token[:-5] + 'abcde',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['code'], K_INVALID_TOKEN)

        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_email_confirmed)

    def test_registration_confirmation_used_token(self):
        '''
        User will get success message if the account has already been confirmed
        '''
        self.user1.is_email_confirmed = True
        self.user1.save()

        url = reverse('auth-register-confirmation')
        data = {
            'token': self.user1.confirmation_token,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['code'], K_REGISTRATION_CONFIRMATION_SUCCESSFUL)

        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_email_confirmed)
