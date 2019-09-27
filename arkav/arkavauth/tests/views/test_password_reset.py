from arkav.arkavauth.models import PasswordResetAttempt
from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import UserSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PasswordResetTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('yonas@gmail.com', 'password',
                                              full_name='Yonas Adiel',
                                              is_email_confirmed=True)
        self.user2 = User.objects.create_user('nella@gmail.com', 'password')

    def test_password_reset(self):
        '''
        User try to reset password
        An attempt will be created with sent_time is not None, used_time is None
        Token should be generated
        '''
        url = reverse('auth-password-reset')
        data = {
            'email': 'yonas@gmail.com',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # TODO: create the test

    def test_password_reset_invalid_email(self):
        '''
        Even if the email is not found, we won't give an error message
        So no one can bruteforce the email
        '''
        # TODO: create the test
        pass

    def test_password_reset_many_times(self):
        '''
        First time user try to reset password, an attempt will be created.
        Every next time an user reset password, the attempt should be at most one attempt.
        If previous attempt exist, the attempt will be refreshed, not creatin new one.
        '''
        # TODO: create the test
        pass


class PasswordResetConfirmationTestCase(APITestCase):
    def setUp(self):
        pass

    def test_password_reset_confirmation(self):
        '''
        When the token is used, password will be replace by new password
        used_time of attempt wont be None anymore
        Plus, if the current user is not confirmed, it will be confirmed too.
        '''
        # TODO: create the test
        pass

    def test_password_reset_confirmation_wrong_token(self):
        '''
        User will get error message if the token is wrong
        '''
        # TODO: create the test
        pass

    def test_password_reset_confirmation_used_token(self):
        '''
        User will get error message if the token has been already used
        '''
        # TODO: create the test
        pass
