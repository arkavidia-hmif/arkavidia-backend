from arkav.arkavauth.models import PasswordResetAttempt
from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import UserSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SessionTestCase(APITestCase):
    def setUp(self):
        pass

    def test_session(self):
        '''
        Will get user session
        '''
        pass
        # TODO: create the test

    def test_session_not_logged_in(self):
        '''
        If the user is not logged in, will get 403
        '''
        # TODO: create the test
        pass
