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
        pass
        # TODO: create the test

    def test_registration_used_email(self):
        '''
        If the email is already used, the response will be 400
        '''
        # TODO: create the test
        pass

    def test_registration_already_login(self):
        '''
        If the user already login, it cant register
        '''
        # TODO: create the test
        pass


class RegistrationConfirmationTestCase(APITestCase):
    def setUp(self):
        pass

    def test_registration_confirmation(self):
        '''
        User account will be confirmed
        '''
        # TODO: create the test
        pass

    def test_registration_confirmation_wrong_token(self):
        '''
        User will get error message if the token is wrong
        '''
        # TODO: create the test
        pass

    def test_registration_confirmation_used_token(self):
        '''
        User will get success message if the account has already been confirmed
        '''
        # TODO: create the test
        pass
