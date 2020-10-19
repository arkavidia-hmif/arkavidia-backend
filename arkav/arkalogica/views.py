from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from arkav.arkalogica.serializers import SubmissionRespSerializer
from arkav.arkalogica.serializers import SessionSerializer
from arkav.arkalogica.serializers import SessionListSerializer
from arkav.arkalogica.serializers import SubmissionReqSerializer
from arkav.arkalogica.models import Submission, Session


class ListSubmissionsView(generics.ListAPIView):
    serializer_class = SubmissionRespSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user)

    @swagger_auto_schema(operation_summary='Submission List')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ListSessionsView(generics.ListAPIView):
    serializer_class = SessionListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Session.objects.all()

    @swagger_auto_schema(operation_summary='Session List')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class StartSessionView(generics.GenericAPIView):
    serializer_class = SubmissionRespSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Start Session',
                         responses={200: SessionSerializer()})
    def get(self, request, *args, **kwargs):
        pass

class SubmitView(generics.GenericAPIView):
    serializer_class = SubmissionReqSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Submit Submission',
                         responses={200: SubmissionRespSerializer()})
    #@method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        pass
