from arkav.eventcheckin.models import CheckInAttendance
from arkav.utils.exceptions import ArkavAPIException
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template import Context
from django.template import Template
from django.utils import timezone
from rest_framework import status
import django_rq
import logging


logger = logging.getLogger(__name__)


class CheckInService():

    @transaction.atomic
    def checkin(self, token, password=''):
        try:
            attendance = CheckInAttendance.objects.get(token=token)
        except CheckInAttendance.DoesNotExist:
            raise ArkavAPIException(
                detail='Attendance token does not exist',
                code='wrong_token',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if attendance.is_fully_checked_in:
            raise ArkavAPIException(
                detail='Attendee can only check in once',
                code='attendee_already_checkin',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if attendance.event.password != password:
            raise ArkavAPIException(
                detail='Wrong Password',
                code='wrong_event_password',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        attendance.pax_checked_in += 1
        attendance.save()
        return attendance

    def send_email(self, attendance, subject, mail_text_message, mail_html_message):
        mail_to = attendance.attendee.email

        mail = EmailMultiAlternatives(
            subject=subject,
            body=mail_text_message,
            to=[mail_to],
        )
        mail.attach_alternative(mail_html_message, 'text/html')
        try:
            mail.send()
            attendance.last_sent_token = timezone.now()
            attendance.save()
        except Exception as e:
            logger.error('Error mailing {} with subject {}'.format(mail_to, subject))
            raise e

    def send_templated_email(self, attendance, subject_template, text_template, html_template):
        subject_template = Template(subject_template)
        html_template = Template(html_template)
        text_template = Template(text_template)

        context = Context({
            'event': attendance.event,
            'attendee': attendance.attendee,
            'token': attendance.token,
        })

        mail_subject = subject_template.render(context)
        mail_text_message = text_template.render(context)
        mail_html_message = html_template.render(context)

        self.send_email(
            attendance,
            mail_subject,
            mail_text_message,
            mail_html_message
        )
