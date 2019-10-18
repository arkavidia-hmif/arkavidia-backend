from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import RegistrationRequestSerializer
from arkav.arkavauth.serializers import RegistrationConfirmationRequestSerializer
from arkav.arkavauth.services import UserService
from arkav.utils.permissions import IsNotAuthenticated
from django.db import transaction
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.response import Response


@ensure_csrf_cookie
@sensitive_post_parameters('password')
@api_view(['POST'])
@permission_classes((IsNotAuthenticated, ))
def registration_view(request):
    request_serializer = RegistrationRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        user = User.objects.create_user(
            email=request_serializer.validated_data['email'].lower(),
            password=request_serializer.validated_data['password'],
            full_name=request_serializer.validated_data['full_name'],
        )

        UserService().send_email(user)

    return Response({
        'code': 'registration_successful',
        'detail': 'Email confirmation link has been sent to your email.'
    })


@ensure_csrf_cookie
@api_view(['POST'])
@permission_classes((IsNotAuthenticated, ))
def registration_confirmation_view(request):
    request_serializer = RegistrationConfirmationRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    token = request_serializer.validated_data['token']

    with transaction.atomic():
        user = User.objects.filter(confirmation_token=token).first()
        if user is None:
            return Response({
                'code': 'invalid_token',
                'detail': 'Invalid token.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user.is_confirmed:
            user.is_email_confirmed = True
            user.save()

    return Response({
        'code': 'registration_confirmation_successful',
        'detail': 'Your email has been successfully confirmed.'
    })
