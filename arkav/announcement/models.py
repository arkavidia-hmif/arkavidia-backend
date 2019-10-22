from arkav.arkavauth.models import User
from django.db import models


class Announcement(models.Model):
    """
    Announcement for competition related
    """
    user = models.ForeignKey(to=User, related_name='announcements', on_delete=models.CASCADE)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
