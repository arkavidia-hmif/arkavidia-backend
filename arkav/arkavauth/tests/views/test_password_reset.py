from arkav.arkavauth.constants import K_INVALID_TOKEN
from arkav.arkavauth.constants import K_PASSWORD_RESET_EMAIL_SENT
from arkav.arkavauth.constants import K_PASSWORD_RESET_SUCCESSFUL
from arkav.arkavauth.constants import K_TOKEN_USED
from arkav.arkavauth.models import PasswordResetAttempt
from arkav.arkavauth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase


class PasswordResetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('yonas@gmail.com', 'password',
                                             full_name='Yonas Adiel',
                                             is_email_confirmed=True)

    def test_password_reset(self):
        '''
        User try to reset password
        An attempt will be created with sent_time is not None, used_time is None
        Token should be generated
        '''
        url = reverse('auth-password-reset')
        data = {
            'email': self.user.email,
        }
        res = self.client.post(url, data=data, format='json')

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['code'], K_PASSWORD_RESET_EMAIL_SENT)
        self.assertEqual(hasattr(self.user, 'password_reset_attempt'), True)

    def test_password_reset_invalid_email(self):
        '''
        Even if the email is not found, we won't give an error message
        So no one can bruteforce the email
        '''
        url = reverse('auth-password-reset')
        data = {
            'email': 'nonexistent@example.org',
        }
        res = self.client.post(url, data=data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['code'], K_PASSWORD_RESET_EMAIL_SENT)

    def test_password_reset_many_times(self):
        '''
        First time user try to reset password, an attempt will be created.
        Every next time an user reset password, the attempt should be at most one attempt.
        Previous attempt will be replaced and rendered unusable by the new attempt.
        '''
        token_initial = PasswordResetAttempt.objects.create(user=self.user).token

        url = reverse('auth-password-reset')
        data = {
            'email': self.user.email,
        }
        res = self.client.post(url, data=data, format='json')

        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['code'], K_PASSWORD_RESET_EMAIL_SENT)
        self.assertEqual(hasattr(self.user, 'password_reset_attempt'), True)
        self.assertNotEqual(self.user.password_reset_attempt.token, token_initial)


class PasswordResetConfirmationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('nella@gmail.com', 'password')

    def test_password_reset_confirmation(self):
        '''
        When the token is used, password will be replace by new password
        used_time of attempt wont be None anymore
        Plus, if the current user is not confirmed, it will be confirmed too.
        '''
        attempt = PasswordResetAttempt.objects.create(user=self.user)
        password_initial = self.user.password
        new_password = password_initial + '123'

        url = reverse('auth-confirm-password-reset')
        data = {
            'token': attempt.token,
            'new_password': new_password,
        }
        res = self.client.post(url, data=data, format='json')

        attempt.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['code'], K_PASSWORD_RESET_SUCCESSFUL)
        self.assertEqual(attempt.is_used, True)
        self.assertEqual(self.user.is_email_confirmed, True)
        self.assertEqual(self.user.check_password(new_password), True)

    def test_password_reset_confirmation_wrong_token(self):
        '''
        User will get error message if the token is wrong
        '''
        url = reverse('auth-confirm-password-reset')
        data = {
            'token': '1',
            'new_password': 'new_password',
        }
        res = self.client.post(url, data=data, format='json')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['code'], K_INVALID_TOKEN)

    def test_password_reset_confirmation_used_token(self):
        '''
        User will get error message if the token has been already used
        '''
        attempt = PasswordResetAttempt.objects.create(user=self.user)
        attempt.used_time = timezone.now()
        attempt.save()

        password_initial = self.user.password
        new_password = password_initial + '123'

        url = reverse('auth-confirm-password-reset')
        data = {
            'token': attempt.token,
            'new_password': new_password,
        }
        res = self.client.post(url, data=data, format='json')

        attempt.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['code'], K_TOKEN_USED)
