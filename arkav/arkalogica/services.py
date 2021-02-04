from arkav.arkalogica.models import Answer
from arkav.arkalogica.models import Choice
from arkav.arkalogica.models import Session
from arkav.arkalogica.models import Submission
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from django.db import transaction
from arkav.utils.exceptions import ArkavAPIException
import csv
from django.http import HttpResponse


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
    def get_submissions(self, session):
        content = []

        questions_id = []
        # Create header (line 1)
        header = []
        header.append("user")
        if session.questions.count() > 0:
            for q in session.questions.all():
                questions_id.append(q.id)
                header.append('%s' % q)

        content.append(header)

        # Create content (line 2-...)
        all_submissions = session.submission.all()
        for sub in all_submissions:
            user_submission = []
            user_submission.append(sub.user.full_name)
            for q in questions_id:
                ans = Answer.objects.filter(submission__user__id=sub.user.id, question=q).first()
                if ans:
                    user_submission.append(ans.tag)
                else:
                    user_submission.append('-')
            content.append(user_submission)

        return content

    def create_csv(self, content, fileName):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % fileName

        writer = csv.writer(response)
        for c in content:
            writer.writerow(c)

        return response

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
        if (len(answer_data['tag']) == 1):
            choice = get_object_or_404(Choice.objects.all(), question=qt, tag=(answer_data['tag']))
            answer, state = Answer.objects.update_or_create(
                submission=sub, question=qt,
                defaults={"choice": choice}
            )
        elif (Answer.objects.filter(submission=sub, question=qt).exists()):
            Answer.objects.filter(submission=sub, question=qt).delete()
        sub.save()  # Untuk update waktu terakhir kali ngerjain (end_time)
        return sub
