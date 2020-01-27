from arkav.eventcheckin.models import CheckInAttendee
from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.models import CheckInEvent
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase


class EventCheckInTestCase(APITestCase):
    def setUp(self):
        self.attendee = CheckInAttendee.objects.create(name='attendee', email='attendee')
        self.event1 = CheckInEvent.objects.create(name='event1')
        self.event2 = CheckInEvent.objects.create(name='event2')
        self.attendance_unattended = CheckInAttendance.objects.create(attendee=self.attendee, event=self.event1)
        self.attendance_attended = CheckInAttendance.objects.create(
            attendee=self.attendee, event=self.event2, checkin_time=timezone.now())

    def test_checkin_unattended(self):
        '''
        Check-in an attendee which has not checked in before to an event
        '''
        url = reverse('attendee-checkin')
        data = {
            'token': self.attendance_unattended.token,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.attendance_unattended.refresh_from_db()
        self.assertTrue(self.attendance_unattended.is_checked_in)

    def test_checkin_already_attended(self):
        '''
        Checking-in an attendee which has checked in to an event before returns an error
        and checkin_time remains unchanged
        '''
        initial_checkin_time = self.attendance_attended.checkin_time
        url = reverse('attendee-checkin')
        data = {
            'token': self.attendance_attended.token,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.attendance_attended.refresh_from_db()
        self.assertEqual(initial_checkin_time, self.attendance_attended.checkin_time)

    def test_checkin_wrong_token(self):
        '''
        Checking-in with an inexistent token returns an error and checkin_time remains unchanged
        '''
        initial_checkin_time = self.attendance_attended.checkin_time
        url = reverse('attendee-checkin')
        data = {
            'token': 'inexistent',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.attendance_attended.refresh_from_db()
        self.assertEqual(initial_checkin_time, self.attendance_attended.checkin_time)
