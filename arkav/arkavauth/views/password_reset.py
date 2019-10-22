from arkav.arkavauth.constants import K_INVALID_TOKEN
from arkav.arkavauth.constants import K_PASSWORD_RESET_EMAIL_SENT
from arkav.arkavauth.constants import K_PASSWORD_RESET_SUCCESSFUL
from arkav.arkavauth.constants import K_TOKEN_USED
from arkav.arkavauth.models import User
from arkav.arkavauth.models import PasswordResetAttempt
from arkav.arkavauth.serializers import PasswordResetRequestSerializer
from arkav.arkavauth.serializers import PasswordResetConfirmationRequestSerializer
from arkav.arkavauth.services import UserService
from arkav.arkavauth.views.openapi.password_reset import password_reset_responses
from arkav.arkavauth.views.openapi.password_reset import password_reset_confirmation_responses
from arkav.utils.permissions import IsNotAuthenticated
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class PasswordResetView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (IsNotAuthenticated, )

    @swagger_auto_schema(responses=password_reset_responses, operation_summary='Password Reset')
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        email = request_serializer.validated_data['email'].lower()

        with transaction.atomic():
            user = User.objects.filter(email=email).first()
            if user is not None:
                # Overwrite existing password reset confirmation attempt, if present
                if hasattr(user, 'password_reset_confirmation_attempt'):
                    user.password_reset_confirmation_attempt.delete()
                attempt = PasswordResetAttempt.objects.create(user=user)
                UserService().send_password_reset_email(attempt)

        return Response(
            {
                'code': K_PASSWORD_RESET_EMAIL_SENT,
                'detail':
                    'If you have registered using that email, we have sent password reset link to your email.'
                    ' Please check your email.',
            }
        )


class PasswordResetConfirmationView(GenericAPIView):
    serializer_class = PasswordResetConfirmationRequestSerializer
    permission_classes = (IsNotAuthenticated, )

    @swagger_auto_schema(responses=password_reset_confirmation_responses,
                         operation_summary='Password Reset Confirmation')
    @method_decorator(ensure_csrf_cookie)
    @method_decorator(sensitive_post_parameters('new_password'))
    def post(self, request):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        token = request_serializer.validated_data['token']
        new_password = request_serializer.validated_data['new_password']

        with transaction.atomic():
            attempt = PasswordResetAttempt.objects.filter(token=token).first()
            if attempt is None:
                return Response(
                    {
                        'code': K_INVALID_TOKEN,
                        'detail': 'Invalid token.',
                    }, status=status.HTTP_400_BAD_REQUEST)

            if attempt.is_confirmed:
                return Response(
                    {
                        'code': K_TOKEN_USED,
                        'detail': 'This token has been used.',
                    }, status=status.HTTP_400_BAD_REQUEST)

            attempt.user.set_password(new_password)
            # Also confirm this user's email, for backward compatibility
            attempt.user.is_email_confirmed = True
            attempt.user.save()
            attempt.is_confirmed = True
            attempt.save()

        return Response({
            'code': K_PASSWORD_RESET_SUCCESSFUL,
            'detail': 'Your password has been successfully reset.',
        })
