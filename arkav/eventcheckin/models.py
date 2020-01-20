from django.db import models
import uuid


class CheckInAttendee(models.Model):
    """
    Subject attending one or more CheckInEvent
    """
    name = models.CharField(max_length=75)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class CheckInEvent(models.Model):
    """
    Event related to the check in process
    """
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class CheckInAttendance(models.Model):
    """
    Many-to-many through/pivot table of CheckInEvent to CheckInAttendee
    """
    event = models.ForeignKey(to=CheckInEvent, related_name='event_attendee', on_delete=models.CASCADE)
    attendee = models.ForeignKey(to=CheckInAttendee, related_name='event_attendee', on_delete=models.CASCADE)

    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    checkin_time = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    @property
    def is_checked_in(self):
        return self.checkin_time is not None

    class Meta:
        get_latest_by = 'checkin_time'

    def __str__(self):
        return '{} - {}'.format(self.attendee, self.event)
