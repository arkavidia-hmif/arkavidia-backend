from arkav.arkavauth.serializers import UserSerializer
from arkav.arkavauth.serializers import PasswordChangeRequestSerializer
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@sensitive_post_parameters('password', 'new_password')
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def password_change_view(request):
    request_serializer = PasswordChangeRequestSerializer(data=request.data)
    request_serializer.is_valid(raise_exception=True)
    password = request_serializer.validated_data['password']
    new_password = request_serializer.validated_data['new_password']

    if not request.user.check_password(password):
        return Response(
            {
                'code': 'password_change_failed',
                'detail': 'Wrong old password.',
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    request.user.set_password(new_password)
    request.user.save()

    return Response({
        'code': 'password_change_successful',
        'detail': 'Your password has been changed.'
    })


@api_view(['PATCH'])
@permission_classes((IsAuthenticated, ))
def edit_user_view(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(data=serializer.data)
