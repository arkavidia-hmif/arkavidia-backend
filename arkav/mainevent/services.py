from arkav.mainevent.models import Task
from arkav.mainevent.models import TaskResponse
from arkav.mainevent.models import Registrant
from arkav.utils.exceptions import ArkavAPIException
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from rest_framework import status
import django_rq


class RegistrantService:

    def send_reminder_email(self, registrant):
        need_to_notify = []
        for task in registrant.active_stage.tasks.all():
            task_response_count = registrant.task_responses.filter(
                task__stage=registrant.active_stage,
                status__in=[TaskResponse.COMPLETED, TaskResponse.AWAITING_VALIDATION],
                task__id=task.id).count()
            if(not task_response_count):
                need_to_notify.append(task)

        context = {
            'name': registrant.user.full_name,
            'active_stage': registrant.active_stage,
            'tasks': need_to_notify,
        }
        text_template = get_template('mainevent_registrant_reminder_email.txt')
        html_template = get_template('mainevent_registrant_reminder_email.html')
        mail_text_message = text_template.render(context)
        mail_html_message = html_template.render(context)

        mail = EmailMultiAlternatives(
            subject='Reminder Main Event Arkavidia 6.0',
            body=mail_text_message,
            to=[registrant.user.email],
        )
        mail.attach_alternative(mail_html_message, 'text/html')
        django_rq.enqueue(mail.send)

    def send_custom_email(self, registrants, subject, mail_text_message, mail_html_message):
        for registrant in registrants.all():
            addresses = [registrant.user.email]

            mail = EmailMultiAlternatives(
                subject=subject,
                body=mail_text_message,
                to=addresses,
            )
            mail.attach_alternative(mail_html_message, 'text/html')
            django_rq.enqueue(mail.send)

    @transaction.atomic
    def create_registrant(self, registrant_data, user):
        mainevent = registrant_data['mainevent_id']

        # Only register if registration is open for this mainevent
        if not mainevent.is_registration_open:
            raise ArkavAPIException(
                detail='The event you are trying to register to is not open for registration.',
                code='mainevent_registration_closed',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # A user can't register in a mainevent if he/she already participated in the same mainevent
        if Registrant.objects.filter(mainevent=mainevent, user=user).exists():
            raise ArkavAPIException(
                detail='One user can only participate in one registrant per main event.',
                code='mainevent_already_registered',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Create a new registrant led by the current user
            new_registrant = Registrant.objects.create(
                mainevent=mainevent,
                user=user,
            )
        except ValueError as e:
            raise ArkavAPIException(
                detail=str(e),
                code='create_registrant_fail',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return new_registrant


class TaskResponseService:

    @transaction.atomic
    def submit_task_response(self, task_response_data, registrant_id, task_id, user):
        # Only registrant members can submit a response
        registrant = get_object_or_404(
            Registrant.objects.all(),
            id=registrant_id,
            user=user,
        )

        if not registrant.is_participating:
            raise ArkavAPIException(
                detail='Your registrant is no longer participating in this main event.',
                code='registrant_not_participating',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # A registrant can only respond to tasks in the currently active stage
        task = get_object_or_404(
            Task.objects.all(),
            id=task_id,
            stage=registrant.active_stage,
        )

        response = task_response_data['response']

        # Create or update this TaskResponse, setting its status to awaiting_validation or completed
        # according to the whether this task requires validation,
        # and also updating its last_submitted_at.
        if task.requires_validation:
            task_response_status = TaskResponse.AWAITING_VALIDATION
        else:
            task_response_status = TaskResponse.COMPLETED

        new_task_response, _ = TaskResponse.objects.update_or_create(
            task=task,
            registrant=registrant,
            defaults={
                'response': response,
                'status': task_response_status,
                'last_submitted_at': timezone.now(),
            },
        )

        return new_task_response
