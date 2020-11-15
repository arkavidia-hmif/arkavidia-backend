from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from arkav.arkalogica.serializers import QuestionSerializer, SubmissionSerializer
from arkav.arkalogica.serializers import AnswerReqSerializer
from arkav.arkalogica.serializers import SessionSerializer
from arkav.arkalogica.models import Submission
from arkav.utils.exceptions import ArkavAPIException
from arkav.arkalogica.services import ArkalogicaService


class SubmissionView(generics.ListAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user)

    @swagger_auto_schema(operation_summary='User Submission''s Answer List')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StartView(generics.GenericAPIView):
    serializer_class = SessionSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Start & Get Questions')
    def get(self, request, *args, **kwargs):
        try:
            questions = ArkalogicaService().get_questions(
                self.kwargs['session_id'],
                request.user
            )
            question_serializers = []
            for q in questions:
                choices = ArkalogicaService().get_choices(q.id)
                q_serializer = QuestionSerializer(choices, many=True)
                question_serializers.append(q_serializer)

            response_serializer = SessionSerializer(question_serializers, many=True)
            return Response(data=response_serializer.data)
        except ArkavAPIException as e:
            return e.as_response()


class SubmitView(generics.GenericAPIView):
    serializer_class = AnswerReqSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Submit Answer',
                         responses={200: SubmissionSerializer()})
    def post(self, request, *args, **kwargs):
        pass
