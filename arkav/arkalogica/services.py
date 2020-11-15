from arkav.arkalogica.models import Session
from arkav.arkalogica.models import Choice
from arkav.arkalogica.models import Question
from arkav.arkalogica.models import Submission
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from django.db import transaction
from arkav.utils.exceptions import ArkavAPIException


class ArkalogicaService:

    @transaction.atomic
    def get_questions(self, session_id, requested_user):
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
        questions = Question.objects.all()
        return questions

    @transaction.atomic
    def get_choices(self, question_id):
        choices = Choice.objects.filter(question=question_id).all()
        return choices
