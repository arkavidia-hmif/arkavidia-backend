from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import UserSerializer
from django.test import TestCase


class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('yonas@gmail.com', 'password',
                                              full_name='Yonas Adiel',
                                              is_email_confirmed=True)

    def test_serializer(self):
        user_data = UserSerializer(self.user1).data
        self.assertEqual(self.user1.full_name, user_data['full_name'])
        self.assertEqual(self.user1.email, user_data['email'])
        self.assertEqual(self.user1.is_staff, user_data['is_staff'])
        self.assertEqual(self.user1.is_active, user_data['is_active'])
        self.assertEqual(self.user1.is_email_confirmed, user_data['is_email_confirmed'])
        self.assertEqual(self.user1.last_login, user_data['last_login'])
        self.assertEqual(self.user1.date_joined.astimezone().isoformat(), user_data['date_joined'])

    def test_serializer_write(self):
        '''
        Some fields in UserSerializer should be read-only
        '''
        pass
