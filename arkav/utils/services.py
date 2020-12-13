
from django.core.mail import EmailMultiAlternatives
import django_rq


class UtilityService():
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
