from arkav.arkalogica.models import Answer
from arkav.arkalogica.models import Choice
from arkav.arkalogica.models import Session
from arkav.arkalogica.models import Submission
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from django.db import transaction
from arkav.utils.exceptions import ArkavAPIException


class ArkalogicaService:

    @transaction.atomic
    def get_session(self, session_id, requested_user):
        session = get_object_or_404(Session.objects.all(), id=session_id)
        if (timezone.now() < session.start_time):
            raise ArkavAPIException(
                detail='This session has not been started.',
                code='is_not_started',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if (timezone.now() > session.end_time):
            raise ArkavAPIException(
                detail='This session has been ended.',
                code='is_ended',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        Submission.objects.update_or_create(user=requested_user)
        return session

    @transaction.atomic
    def get_submission(self, requested_user):
        submission, state = Submission.objects.get_or_create(user=requested_user)
        return submission

    @transaction.atomic
    def submit_answer(self, answer_data, requested_user):
        session = Session.objects.first()
        if (timezone.now() < session.start_time):
            raise ArkavAPIException(
                detail='This session has not been started.',
                code='is_not_started',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if (timezone.now() > session.end_time):
            raise ArkavAPIException(
                detail='This session has been ended.',
                code='is_ended',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        sub, state = Submission.objects.get_or_create(user=requested_user)
        qt = answer_data['question']
        choice = get_object_or_404(Choice.objects.all(), question=qt, tag=(answer_data['tag']))
        answer, state = Answer.objects.update_or_create(
            submission=sub, question=qt,
            defaults={"choice": choice}
        )
        sub.save()  # Untuk update waktu terakhir kali ngerjain (end_time)
        return sub
