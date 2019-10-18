from arkav.arkavauth.models import User
from arkav.announcement.models import Announcement
from arkav.announcement.serializers import AnnouncementSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AnnouncementTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='yonas@gmail.com')
        self.user2 = User.objects.create_user(email='jones@gmail.com')
        self.announcement1 = Announcement.objects.create(user=self.user1, message='announcement 1')
        self.announcement2 = Announcement.objects.create(user=self.user1, message='announcement 2')
        self.announcement3 = Announcement.objects.create(user=self.user2, message='announcement 3')

    def test_list_announcement(self):
        '''
        User will only see his/her own announcement
        '''
        url = reverse('announcement-list')
        self.client.force_authenticate(self.user1)
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res_announcements = res.data
        self.assertEqual(len(res_announcements), Announcement.objects.filter(user=self.user1).count())
        for res_announcement in res_announcements:
            announcement = Announcement.objects.get(message=res_announcement['message'])
            self.assertDictEqual(res_announcement, AnnouncementSerializer(announcement).data)
