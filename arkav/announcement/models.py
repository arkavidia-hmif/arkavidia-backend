from arkav.arkavauth.models import User
from django.db import models


class Announcement(models.Model):
    """
    Announcement for competition related
    """
    user = models.ManyToManyField(to=User, related_name='announcements')
    title = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
