from arkav.competition.models import TeamMember
from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.models import CheckInAttendee
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
        attendance = CheckInAttendance.objects.get(token=checkin_data['token'])

        if attendance.is_checked_in:
            raise ArkavAPIException(
                detail='Attendee can only check in once',
                code='attendee_already_checkin',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            attendance.checkin_time = timezone.now()
            attendance.save()
        except ValueError as e:
            raise ArkavAPIException(
                detail=str(e),
                code='checkin_fail',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return attendance

    @transaction.atomic
    def migrate_teams(self, teams, events):
        members = TeamMember.objects.filter(team__in=teams).distinct()
        attendees = []
        for member in members:
            attendee, _ = CheckInAttendee.objects.get_or_create(
                email=member.email,
                name=member.full_name,
            )
            attendees.append(attendee)
        for event in events:
            CheckInAttendance.objects.bulk_create([CheckInAttendance(
                event=event,
                attendee=attendee,
            ) for attendee in attendees])

    @transaction.atomic
    def migrate_registrants(self, registrants, events):
        attendees = []
        for registrant in registrants:
            attendee, _ = CheckInAttendee.objects.get_or_create(
                email=registrant.user.email,
                name=registrant.user.full_name,
            )
            attendees.append(attendee)
        for event in events:
            CheckInAttendance.objects.bulk_create([CheckInAttendance(
                event=event,
                attendee=attendee,
            ) for attendee in attendees])

    # def send_email(self, attendee, subject, context, text_template, html_template):
    #     mail_text_message = text_template.render(context)
    #     mail_html_message = html_template.render(context)
    #     mail_to = attendee.email

    #     mail = EmailMultiAlternatives(
    #         subject=subject,
    #         body=mail_text_message,
    #         to=[mail_to],
    #     )
    #     mail.attach_alternative(mail_html_message, 'text/html')
    #     try:
    #         django_rq.enqueue(mail.send)
    #     except Exception:
    #         logger.error('Error mailing {} with subject {}'.format(mail_to, subject))

    # def send_token_qr_code(self, attendee):
    #     text_template = get_template('token_qr_code_email.txt')
    #     html_template = get_template('token_qr_code_email.html')

    #     context = {
    #         'token': attendee.token,
    #     }

    #     self.send_email(attendee, '[Arkavidia] Konfirmasi Email', context, text_template, html_template)
