from arkav.eventcheckin.models import CheckInAttendee
from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.models import CheckInEvent
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class EventCheckInTestCase(APITestCase):
    def setUp(self):
        self.attendee = CheckInAttendee.objects.create(name='attendee', email='attendee')
        self.event1 = CheckInEvent.objects.create(name='event1', password='event1')
        self.event2 = CheckInEvent.objects.create(name='event2', password='event2')
        self.attendance_unattended = CheckInAttendance.objects.create(
            attendee=self.attendee, event=self.event1, pax=2, pax_checked_in=1)
        self.attendance_attended = CheckInAttendance.objects.create(
            attendee=self.attendee, event=self.event2, pax=2, pax_checked_in=2)

    def test_checkin_get(self):
        '''
        Check for the check in data
        '''
        original_pax_checked_in = self.attendance_unattended.pax_checked_in
        url = reverse('attendee-checkin', kwargs={'token': self.attendance_unattended.token})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        checkin_data = res.json()
        self.assertEqual(checkin_data['attendeeName'], self.attendance_unattended.attendee.name)
        self.assertEqual(checkin_data['attendeeEmail'], self.attendance_unattended.attendee.email)
        self.assertEqual(checkin_data['pax'], self.attendance_unattended.pax)
        self.assertEqual(checkin_data['event'], self.attendance_unattended.event.name)
        self.assertEqual(checkin_data['paxCheckedIn'], self.attendance_unattended.pax_checked_in)
        self.attendance_unattended.refresh_from_db()
        self.assertEqual(original_pax_checked_in, self.attendance_unattended.pax_checked_in)

    def test_checkin_get_invalid_token(self):
        '''
        Check for the check in data
        '''
        url = reverse('attendee-checkin', kwargs={'token': 'e19a1e6d-3375-4fff-9006-a02243fe8cda'})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkin_unattended(self):
        '''
        Check-in an attendee which has not checked in before to an event
        '''
        url = reverse('attendee-checkin', kwargs={'token': self.attendance_unattended.token})
        data = {
            'password': self.attendance_unattended.event.password,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.attendance_unattended.refresh_from_db()
        self.assertTrue(self.attendance_unattended.is_fully_checked_in)

    def test_checkin_unattended_twice(self):
        '''
        Check-in an attendee which has not checked in before to an event
        '''
        self.attendance_unattended.pax_checked_in = 0
        self.attendance_unattended.save()
        url = reverse('attendee-checkin', kwargs={'token': self.attendance_unattended.token})
        data = {
            'password': self.attendance_unattended.event.password,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.attendance_unattended.refresh_from_db()
        self.assertFalse(self.attendance_unattended.is_fully_checked_in)

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.attendance_unattended.refresh_from_db()
        self.assertTrue(self.attendance_unattended.is_fully_checked_in)

    def test_checkin_unattended_wrong_password(self):
        '''
        Check-in an attendee with wrong password
        '''
        url = reverse('attendee-checkin', kwargs={'token': self.attendance_unattended.token})
        data = {
            'password': 'wrong-password',
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.attendance_unattended.refresh_from_db()
        self.assertFalse(self.attendance_unattended.is_fully_checked_in)

    def test_checkin_already_attended(self):
        '''
        Checking-in an attendee which has checked in to an event before returns an error
        '''
        self.assertEqual(self.attendance_attended.pax, self.attendance_attended.pax_checked_in)
        url = reverse('attendee-checkin', kwargs={'token': self.attendance_attended.token})
        data = {
            'password': self.attendance_attended.event.password,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.attendance_attended.refresh_from_db()
        self.assertEqual(self.attendance_attended.pax, self.attendance_attended.pax_checked_in)

    def test_checkin_wrong_token(self):
        '''
        Checking-in with an inexistent token returns an error
        '''
        url = reverse('attendee-checkin', kwargs={'token': 'e19a1e6d-3375-4fff-9006-a02243fe8cda'})
        data = {
            'password': self.attendance_attended.event.password,
        }
        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
