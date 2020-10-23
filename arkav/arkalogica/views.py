from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from arkav.arkalogica.serializers import SubmissionSerializer
from arkav.arkalogica.serializers import AnswerReqSerializer
from arkav.arkalogica.serializers import SessionSerializer
from arkav.arkalogica.models import Submission


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

    @swagger_auto_schema(operation_summary='Start')
    def get(self, request, *args, **kwargs):
        pass


class SubmitView(generics.GenericAPIView):
    serializer_class = AnswerReqSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Submit Answer',
                         responses={200: SubmissionSerializer()})
    def post(self, request, *args, **kwargs):
        pass
