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

    @swagger_auto_schema(operation_summary='Check in',
                         responses={200: CheckInResponseSerializer()})
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        request_serializer = CheckInRequestSerializer(data=request.data)
        try:
            request_serializer.is_valid(raise_exception=True)
            checkin_data = CheckInService().checkin(request_serializer.validated_data)
            response_serializer = CheckInResponseSerializer(checkin_data)
            return Response(data=response_serializer.data, status=status.HTTP_200_OK)
        except ArkavAPIException as e:
            return e.as_response()
