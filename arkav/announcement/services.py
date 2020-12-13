from arkav.announcement.models import Announcement
from arkav.announcement.models import AnnouncementUser


class AnnouncementService():

    def send_announcement(self, title, message, users):
        announcement, _ = Announcement.objects.get_or_create(
            title=title,
            message=message,
        )

        announcement_users = [AnnouncementUser(user=user, announcement=announcement) for user in users]
        AnnouncementUser.objects.bulk_create(announcement_users)
