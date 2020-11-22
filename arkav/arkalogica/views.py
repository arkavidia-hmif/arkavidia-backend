from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from arkav.arkalogica.serializers import SubmissionSerializer
from arkav.arkalogica.serializers import AnswerReqSerializer
from arkav.arkalogica.serializers import SessionSerializer
from arkav.utils.exceptions import ArkavAPIException
from arkav.arkalogica.services import ArkalogicaService


class SubmissionView(generics.GenericAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='User''s Submission')
    def get(self, request, *args, **kwargs):
        try:
            sub = ArkalogicaService().get_submission(
                request.user
            )
            response_serializer = SubmissionSerializer(sub)
            return Response(data=response_serializer.data)
        except ArkavAPIException as e:
            return e.as_response()


class StartView(generics.GenericAPIView):
    serializer_class = SessionSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Start & Get Questions')
    def get(self, request, *args, **kwargs):
        try:
            session = ArkalogicaService().get_session(
                self.kwargs['session_id'],
                request.user
            )
            response_serializer = SessionSerializer(session)
            return Response(data=response_serializer.data)
        except ArkavAPIException as e:
            return e.as_response()


class SubmitView(generics.GenericAPIView):
    serializer_class = AnswerReqSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Submit Answer',
                         responses={200: SubmissionSerializer()})
    def post(self, request, *args, **kwargs):
        request_serializer = AnswerReqSerializer(data=request.data)
        try:
            request_serializer.is_valid(raise_exception=True)
            submission = ArkalogicaService().submit_answer(
                request_serializer.validated_data,
                request.user
            )
            response_serializer = SubmissionSerializer(submission)
            return Response(data=response_serializer.data)
        except ArkavAPIException as e:
            return e.as_response()
