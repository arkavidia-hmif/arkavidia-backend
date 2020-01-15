from arkav.arkavauth.models import User
from django.db import models
import uuid


class CheckInEvent(models.Model):
    """
    Event related to the check in process
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CheckInAttendee(models.Model):
    """
    Many-to-many through/pivot table of CheckInEvent to Attendee
    """
    event = models.ForeignKey(to=CheckInEvent, related_name='event_user', on_delete=models.CASCADE)
    name = models.CharField(max_length=75)
    email = models.EmailField(unique=True)
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    checkin_time = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    @property
    def is_checkin(self):
        return self.checkin_time is None

    class Meta:
        get_latest_by = 'checkin_time'
