from arkav.arkavauth.constants import K_INVALID_TOKEN
from arkav.arkavauth.constants import K_REGISTRATION_SUCCESSFUL
from arkav.arkavauth.constants import K_REGISTRATION_CONFIRMATION_SUCCESSFUL
from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import RegistrationRequestSerializer
from arkav.arkavauth.serializers import RegistrationConfirmationRequestSerializer
from arkav.arkavauth.services import UserService
from arkav.arkavauth.views.openapi.registration import registration_responses
from arkav.arkavauth.views.openapi.registration import registration_confirmation_responses
from arkav.utils.permissions import IsNotAuthenticated
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class RegistrationView(GenericAPIView):
    serializer_class = RegistrationRequestSerializer
    permission_classes = (IsNotAuthenticated, )

    @swagger_auto_schema(responses=registration_responses, operation_summary='Registration')
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            user = User.objects.create_user(
                email=request_serializer.validated_data['email'].lower(),
                password=request_serializer.validated_data['password'],
                full_name=request_serializer.validated_data['full_name'],
            )

            UserService().send_registration_confirmation_email(user)

        return Response({
            'code': K_REGISTRATION_SUCCESSFUL,
            'detail': 'Email confirmation link has been sent to your email.',
        })


class RegistrationConfirmationView(GenericAPIView):
    serializer_class = RegistrationConfirmationRequestSerializer
    permission_classes = (IsNotAuthenticated, )

    @swagger_auto_schema(responses=registration_confirmation_responses, operation_summary='Registration Confirmation')
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        token = request_serializer.validated_data['token']

        with transaction.atomic():
            user = User.objects.filter(confirmation_token=token).first()
            if user is None:
                return Response({
                    'code': K_INVALID_TOKEN,
                    'detail': 'Invalid token.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not user.is_email_confirmed:
                user.is_email_confirmed = True
                user.save()

        return Response({
            'code': K_REGISTRATION_CONFIRMATION_SUCCESSFUL,
            'detail': 'Your email has been successfully confirmed.'
        })
