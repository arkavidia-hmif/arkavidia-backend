from arkav.eventcheckin.models import CheckInEvent
from arkav.eventcheckin.models import CheckInAttendee
from arkav.utils.exceptions import ArkavAPIException
from django.utils import timezone
from rest_framework import status


class CheckInService():

    def checkin(self, user):
        attendee = CheckInAttendee.objects.get(token=user['token'])

        if attendee.checkin_time:
            raise ArkavAPIException(
                detail='Attendee can only check in once',
                code='attendee_already_checkin',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            attendee.checkin_time = timezone.now()
            attendee.save()

        except ValueError as e:
            raise ArkavAPIException(
                detail=str(e),
                code='checkin_fail',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return attendee
