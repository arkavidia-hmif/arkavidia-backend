from arkav.arkavauth.models import User
from arkav.announcement.services import AnnouncementService
from django.test import TestCase


class AnnouncementServiceTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='yonas@gmail.com')
        self.user2 = User.objects.create_user(email='jones@gmail.com')

    def test_send_announcement(self):
        AnnouncementService().send_announcement(title='A1', message='announcement1', users=User.objects.all())
        AnnouncementService().send_announcement(title='A2', message='announcement2',
                                                users=User.objects.filter(email='yonas@gmail.com'))
        AnnouncementService().send_announcement(title='A3', message='announcement3',
                                                users=User.objects.filter(email='jones@gmail.com'))

        self.assertIsNotNone(self.user1.announcements.filter(title='A1').first())
        self.assertIsNotNone(self.user1.announcements.filter(title='A2').first())
        self.assertIsNone(self.user1.announcements.filter(title='A3').first())

        self.assertIsNotNone(self.user2.announcements.filter(title='A1').first())
        self.assertIsNone(self.user2.announcements.filter(title='A2').first())
        self.assertIsNotNone(self.user2.announcements.filter(title='A3').first())
