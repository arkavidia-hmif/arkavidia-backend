from arkav.arkavauth.constants import K_PASSWORD_CHANGE_FAILED
from arkav.arkavauth.constants import K_PASSWORD_CHANGE_SUCCESSFUL
from arkav.arkavauth.models import User
from datetime import date
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
        self.assertEqual(res.data['code'], K_PASSWORD_CHANGE_SUCCESSFUL)
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
        self.assertEqual(res.data['code'], K_PASSWORD_CHANGE_FAILED)
        failedLogin = self.client.login(username='yonas@gmail.com', password='wrong_password')
        self.assertFalse(failedLogin)
        failedLogin = self.client.login(username='yonas@gmail.com', password='new_password')
        self.assertFalse(failedLogin)
        successLogin = self.client.login(username='yonas@gmail.com', password='password')
        self.assertTrue(successLogin)

    def test_password_change_unauthorized(self):
        '''
        If the user hasnt been login, it wont be processed
        '''
        url = reverse('auth-change-password')
        data = {
            'password': 'password',
            'new_password': 'new_password',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


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
            'currentEducation': 'ABCDEFGHIJKLM',
            'institution': 'SMA 3 Bandung',
            'phoneNumber': '0877012345678',
            'birthDate': '1998-10-11',
            'address': 'Jl. Ganesa 10',
        }
        res = self.client.patch(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        fullnameAfter = res.data['full_name']
        emailAfter = res.data['email']
        self.assertNotEqual(fullnameBefore, fullnameAfter)
        self.assertEqual(fullnameAfter, data['full_name'])
        self.assertEqual(emailBefore, emailAfter)
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.is_email_confirmed)
        self.assertEqual(self.user.current_education, data['currentEducation'])
        self.assertEqual(self.user.institution, data['institution'])
        self.assertEqual(self.user.phone_number, data['phoneNumber'])
        self.assertEqual(str(self.user.birth_date), data['birthDate'])
        self.assertEqual(self.user.address, data['address'])

    def test_edit_user_minimum(self):
        '''
        Not all fields should be included
        '''
        self.user.current_education = 'COLLEGE'
        self.user.institution = 'ABC'
        self.user.phone_number = '087xxxxxxx'
        self.user.birth_date = date.today()
        self.user.address = 'abcdef'
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
            'currentEducation': None,
            'institution': None,
            'phoneNumber': None,
            'birthDate': None,
            'address': None,
        }
        res = self.client.patch(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        fullnameAfter = res.data['full_name']
        emailAfter = res.data['email']
        self.assertNotEqual(fullnameBefore, fullnameAfter)
        self.assertEqual(fullnameAfter, data['full_name'])
        self.assertEqual(emailBefore, emailAfter)
        self.assertFalse(self.user.is_staff)
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.is_email_confirmed)
        self.assertIsNone(self.user.current_education)
        self.assertIsNone(self.user.institution)
        self.assertIsNone(self.user.phone_number)
        self.assertIsNone(self.user.birth_date)
        self.assertIsNone(self.user.address)

    def test_edit_user_unauthorized(self):
        '''
        Will return 401 if user hasnt logged in
        '''
        url = reverse('auth-edit-user')
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
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(fullnameBefore, self.user.full_name)
        self.assertEqual(emailBefore, self.user.email)

    def test_edit_user_wrong_user(self):
        '''
        Trying to edit other user is equally trying to edit email.
        '''
        user = User.objects.create_user(email='jones@gmail.com', full_name='Jones')
        url = reverse('auth-edit-user')
        self.client.force_authenticate(self.user)
        data = {
            'full_name': 'Jones Napoleon',
            'email': user.email,
        }
        res = self.client.patch(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(user.full_name, 'Jones')
        self.assertEqual(self.user.full_name, data['full_name'])
