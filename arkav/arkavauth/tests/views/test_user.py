from arkav.arkavauth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PasswordChangeTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('yonas@gmail.com', 'password',
                                             full_name='Yonas Adiel',
                                             is_email_confirmed=True)

    def test_password_change(self):
        '''
        Password will be changed
        '''
        url = reverse('auth-change-password')
        self.client.force_authenticate(user=self.user)
        data = {
            'password': 'password',
            'new_password': 'new_password',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['code'], 'password_change_successful')
        failedLogin = self.client.login(username='yonas@gmail.com', password='password')
        self.assertFalse(failedLogin)
        successLogin = self.client.login(username='yonas@gmail.com', password='new_password')
        self.assertTrue(successLogin)

    def test_password_change_invalid_old_password(self):
        '''
        If the old password is wrong, the password won't be changed
        '''
        url = reverse('auth-change-password')
        self.client.force_authenticate(user=self.user)
        data = {
            'password': 'wrong_password',
            'new_password': 'new_password',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.data['code'], 'password_change_failed')
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
            'new_password': 'new_password',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class EditUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('yonas@gmail.com', 'password',
                                             full_name='Yonas Adiel',
                                             is_email_confirmed=True)

    def test_edit_user(self):
        '''
        New user will be sent, but the only field will be changed is
        the on that is read only on serializer
        '''
        url = reverse('auth-edit-user')
        self.client.force_authenticate(user=self.user)
        fullnameBefore = self.user.full_name
        emailBefore = self.user.email
        data = {
            'full_name': 'Jones',
            'email': 'jones@gmail.com',
            'is_staff': True,
            'is_active': False,
            'is_email_confirmed': False,
        }
        res = self.client.patch(url, data=data, format='json')
        fullnameAfter = res.data['full_name']
        emailAfter = res.data['email']
        self.assertNotEqual(fullnameBefore, fullnameAfter)
        self.assertEqual(fullnameAfter, data['full_name'])
        self.assertEqual(emailBefore, emailAfter)
