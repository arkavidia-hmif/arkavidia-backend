from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.serializers import CheckInRequestSerializer
from arkav.eventcheckin.serializers import CheckInResponseSerializer
from arkav.eventcheckin.services import CheckInService
from arkav.utils.exceptions import ArkavAPIException
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response


class CheckInAttendeeView(generics.GenericAPIView):
    serializer_class = CheckInRequestSerializer

    @swagger_auto_schema(operation_summary='Check token',
                         responses={200: CheckInResponseSerializer()})
    def get(self, request, *args, **kwargs):
        try:
            # If the password is passed on url param, we check for which event has the password
            # This enable specific token for specific event, because token for each event may duplicated
            # Example use case, "wild token" that can be used to enter multiple mainevent
            password = request.GET.get('password', None)
            attendance = None
            if password is None:
                attendance = CheckInAttendance.objects.filter(token=self.kwargs['token']).first()
            else:
                attendance = CheckInAttendance.objects.filter(
                    token=self.kwargs['token'], event__password=password
                ).first()
            if attendance is None:
                raise ArkavAPIException(
                    detail='Attendance token does not exist',
                    code='wrong_token',
                    status_code=status.HTTP_404_NOT_FOUND,
                )
            response_serializer = CheckInResponseSerializer(attendance)
            return Response(data=response_serializer.data, status=status.HTTP_200_OK)
        except ArkavAPIException as e:
            return e.as_response()

    @swagger_auto_schema(operation_summary='Check in',
                         responses={200: CheckInResponseSerializer()})
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        request_serializer = CheckInRequestSerializer(data=request.data)
        try:
            request_serializer.is_valid(raise_exception=True)
            checkin_data = CheckInService().checkin(
                self.kwargs['token'],
                request_serializer.validated_data['password'],
            )
            response_serializer = CheckInResponseSerializer(checkin_data)
            return Response(data=response_serializer.data, status=status.HTTP_200_OK)
        except ArkavAPIException as e:
            return e.as_response()
