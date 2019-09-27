from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import UserSerializer
from arkav.arkavauth.serializers import PasswordResetRequestSerializer
from arkav.arkavauth.serializers import PasswordResetConfirmationRequestSerializer
from arkav.arkavauth.serializers import PasswordChangeRequestSerializer
from arkav.utils.permissions import IsNotAuthenticated
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@ensure_csrf_cookie
@api_view(['POST'])
@permission_classes((IsNotAuthenticated, ))
def password_reset_view(request):
    request_serializer = PasswordResetAttemptRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    email = request_serializer.validated_data['email'].lower()

    with transaction.atomic():
        user = User.objects.filter(email=email).first()
        if user is not None:
            # Overwrite existing password reset confirmation attempt, if present
            if hasattr(user, 'password_reset_confirmation_attempt'):
                user.password_reset_confirmation_attempt.delete()
            attempt = PasswordResetConfirmationAttempt.objects.create(user=user)
            attempt.send_email()

    return Response({
        'code': 'password_reset_email_sent',
        'detail':
            'If you have registered using that email, we have sent password reset link to your email.'
            ' Please check your email.'
    })


@ensure_csrf_cookie
@sensitive_post_parameters('new_password')
@api_view(['POST'])
@permission_classes((IsNotAuthenticated, ))
def password_reset_confirmation_view(request):
    request_serializer = PasswordResetConfirmationRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    token = request_serializer.validated_data['token']
    new_password = request_serializer.validated_data['new_password']

    with transaction.atomic():
        attempt = PasswordResetConfirmationAttempt.objects.filter(token=token).first()
        if attempt is None:
            return Response({
                'code': 'invalid_token',
                'detail': 'Invalid token.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if attempt.is_confirmed:
            return Response({
                'code': 'token_used',
                'detail': 'This token has been used.'
            }, status=status.HTTP_400_BAD_REQUEST)

        attempt.user.set_password(new_password)
        # Also confirm this user's email, for backward compatibility
        attempt.user.is_email_confirmed = True
        attempt.user.save()
        attempt.is_confirmed = True
        attempt.save()

    return Response({
        'code': 'password_reset_succesful',
        'detail': 'Your password has been succesfully reset.'
    })
