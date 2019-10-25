from arkav.announcement.models import Announcement


class AnnouncementService():

    def send_announcement(self, title, message, users):
        announcement = Announcement.objects.create(title=title, message=message)
        UserAnnouncement = Announcement.user.through

        user_announcements = [UserAnnouncement(user_id=user.id, announcement_id=announcement.id) for user in users]
        UserAnnouncement.objects.bulk_create(user_announcements)
