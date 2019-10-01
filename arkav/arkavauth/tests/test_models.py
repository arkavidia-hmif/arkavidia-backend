from arkav.arkavauth.models import PasswordResetAttempt
from arkav.arkavauth.models import User
from django.test import TestCase


class UserTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(email='yonas@gmail.com')
        self.user2 = User.objects.create(email='adiel@gmail.com')

    def test_token_always_different(self):
        '''
        User should always have different registration confirmation tokens.
        '''
        self.assertIsNotNone(self.user1.confirmation_token)
        self.assertIsNotNone(self.user2.confirmation_token)
        self.assertNotEqual(self.user1.confirmation_token, self.user2.confirmation_token)


class PasswordResetAttemptTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(email='yonas@gmail.com')
        self.user2 = User.objects.create(email='adiel@gmail.com')

    def test_token_always_different(self):
        '''
        Password reset attempts should always have different tokens.
        '''
        attempt1 = PasswordResetAttempt.objects.create(user=self.user1)
        attempt2 = PasswordResetAttempt.objects.create(user=self.user2)
        self.assertIsNotNone(attempt1.token)
        self.assertIsNotNone(attempt2.token)
        self.assertNotEqual(attempt1.token, attempt2.token)
