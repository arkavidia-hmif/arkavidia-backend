from arkav.arkavauth.models import User
from django.db import models


class Announcement(models.Model):
    """
    Announcement for competition related
    """
    user = models.ManyToManyField(to=User, related_name='announcements', through='AnnouncementUser')
    title = models.CharField(max_length=100, blank=True)
    message = models.TextField()

    def __str__(self):
        return self.title


class AnnouncementUser(models.Model):
    """
    Many-to-many through/pivot table of Announcement to User
    """
    announcement = models.ForeignKey(to=Announcement, related_name='announcement_user', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, related_name='announcement_user', on_delete=models.CASCADE)

    date_sent = models.DateTimeField(auto_now_add=True)

    @property
    def title(self):
        return self.announcement.title

    @property
    def message(self):
        return self.announcement.message

    class Meta:
        get_latest_by = 'date_sent'
