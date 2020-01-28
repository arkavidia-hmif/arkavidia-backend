from arkav.eventcheckin.models import CheckInAttendance
from arkav.utils.exceptions import ArkavAPIException
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.template.loader import get_template
from django.utils import timezone
from rest_framework import status
import django_rq
import logging


logger = logging.getLogger(__name__)


class CheckInService():

    @transaction.atomic
    def checkin(self, checkin_data):
        try:
            attendance = CheckInAttendance.objects.get(token=checkin_data['token'])
        except CheckInAttendance.DoesNotExist:
            raise ArkavAPIException(
                detail='Attendance token does not exist',
                code='wrong_token',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if attendance.is_fully_checked_in:
            raise ArkavAPIException(
                detail='Attendee can only check in once',
                code='attendee_already_checkin',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        attendance.pax_checked_in += 1
        attendance.save()
        return attendance

    def send_email(self, attendance, subject, context, text_template, html_template):
        mail_text_message = text_template.render(context)
        mail_html_message = html_template.render(context)
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
        except Exception:
            logger.error('Error mailing {} with subject {}'.format(mail_to, subject))

    def send_token_qr_code(self, attendance):
        html_template = get_template('token_qr_code_email.html')
        text_template = get_template('token_qr_code_email.txt')

        context = {
            'event': attendance.event,
            'attendee': attendance.attendee,
            'token': attendance.token,
        }

        subject = '[Arkavidia] {} - Check-In QR Code'.format(attendance.event)
        django_rq.enqueue(
            self.send_email,
            attendance,
            subject,
            context,
            text_template,
            html_template
        )
