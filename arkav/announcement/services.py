from arkav.announcement.models import Announcement
from arkav.announcement.models import AnnouncementUser
from django.core.mail import EmailMultiAlternatives
import django_rq


class AnnouncementService():

    def send_announcement(self, title, message, users):
        announcement, _ = Announcement.objects.get_or_create(
            title=title,
            message=message,
        )

        announcement_users = [AnnouncementUser(user=user, announcement=announcement) for user in users]
        AnnouncementUser.objects.bulk_create(announcement_users)

    def send_custom_email(self, addresses, subject, mail_text_message, mail_html_message, attachments):
        mail = EmailMultiAlternatives(
            subject=subject,
            body=mail_text_message,
            to=addresses,
        )
        mail.attach_alternative(mail_html_message, 'text/html')
        for attachment in attachments:
            mail.attach_file(attachment)
        django_rq.enqueue(mail.send)
