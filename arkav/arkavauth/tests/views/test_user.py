from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import UserSerializer
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


class PasswordChangeTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('yonas@gmail.com', 'password',
                                              full_name='Yonas Adiel',
                                              is_email_confirmed=True)
        self.user2 = User.objects.create_user('nella@gmail.com', 'password')

    def test_password_change(self):
        '''
        Password will be changed
        '''
        url = reverse('auth-change-password')
        self.client.force_authenticate(user=self.user1)
        data = {
            'password': 'password',
            'new_password': 'new_password'
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['code'], 'password_change_successful')
        self.assertEqual(res.data['detail'], 'Your password has been changed.')

        failedLogin = self.client.login(username='yonas@gmail.com', password='password')
        self.assertFalse(failedLogin)
        successLogin = self.client.login(username='yonas@gmail.com', password='new_password')
        self.assertTrue(successLogin)

    def test_password_change_invalid_old_password(self):
        '''
        If the old password is wrong, the password won't be changed
        '''
        url = reverse('auth-change-password')
        self.client.force_authenticate(user=self.user1)
        data = {
            'password': 'wrong_password',
            'new_password': 'new_password'
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.data['code'], 'password_change_failed')
        self.assertEqual(res.data['detail'], 'Wrong old password.')
        failedLogin = self.client.login(username='yonas@gmail.com', password='wrong_password')
        self.assertFalse(failedLogin)
        failedLogin = self.client.login(username='yonas@gmail.com', password='new_password')
        self.assertFalse(failedLogin)
        successLogin = self.client.login(username='yonas@gmail.com', password='password')
        self.assertTrue(successLogin)

    def test_password_change_not_logged_in(self):
        '''
        If the user hasnt been login, it wont be processed
        '''
        url = reverse('auth-change-password')
        data = {
            'password': 'password',
            'new_password': 'new_password'
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class EditUserTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('yonas@gmail.com', 'password',
                                              full_name='Yonas Adiel',
                                              is_email_confirmed=True)
        self.user2 = User.objects.create_user('nella@gmail.com', 'password')

    def test_edit_user(self):
        '''
        New user will be sent, but the only field will be changed is
        the on that is read only on serializer
        '''
        url = reverse('auth-edit-user')
        self.client.force_authenticate(user=self.user1)
        fullnameBefore = UserSerializer(self.user1).data['full_name']
        emailBefore = UserSerializer(self.user1).data['email']
        data = {
            'full_name': 'Jones',
            'email': 'jones@gmail.com',
            'is_staff': True,
            'is_active': False,
            'is_email_confirmed': False
        }
        res = self.client.patch(url, data=data, format='json')
        fullnameAfter = res.data['full_name']
        emailAfter = res.data['email']
        self.assertNotEqual(fullnameBefore, fullnameAfter)
        self.assertEqual(fullnameAfter, 'Jones')
        self.assertEqual(emailBefore, emailAfter)
        self.assertEqual(emailAfter, 'yonas@gmail.com')
