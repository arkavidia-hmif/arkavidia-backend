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
    last_sent_token = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    pax = models.IntegerField(default=1)
    pax_checked_in = models.IntegerField(default=0)

    @property
    def is_fully_checked_in(self):
        return self.pax == self.pax_checked_in

    @property
    def is_token_sent(self):
        return self.last_sent_token is not None

    def __str__(self):
        return '{} - {}'.format(self.attendee, self.event)
