from arkav.arkavauth.models import PasswordResetAttempt
from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import UserSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class PasswordChangeTestCase(APITestCase):
    def setUp(self):
        pass

    def test_password_change(self):
        '''
        Password will be changed
        '''
        pass
        # TODO: create the test

    def test_password_change_invalid_old_password(self):
        '''
        If the old password is wrong, the password won't be changed
        '''
        # TODO: create the test
        pass

    def test_password_change_not_logged_in(self):
        '''
        If the user hasnt been login, it wont be processed
        '''
        # TODO: create the test
        pass


class EditUserTestCase(APITestCase):
    def setUp(self):
        pass

    def test_edit_user(self):
        '''
        New user will be sent, but the only field will be changed is
        the on that is read only on serializer
        '''
        # TODO: create the test
        pass

    def test_edit_user_wrong_user(self):
        '''
        User won't be able to change other user data
        '''
        # TODO: create the test
        pass
