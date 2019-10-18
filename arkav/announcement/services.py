from arkav.announcement.models import Announcement


class AnnouncementService():

    def send_announcement(self, user, message):
        Announcement.objects.create(message=message, user=user)
