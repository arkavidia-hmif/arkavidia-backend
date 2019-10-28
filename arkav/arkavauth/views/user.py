from arkav.arkavauth.constants import K_PASSWORD_CHANGE_FAILED
from arkav.arkavauth.constants import K_PASSWORD_CHANGE_SUCCESSFUL
from arkav.arkavauth.serializers import UserSerializer
from arkav.arkavauth.serializers import PasswordChangeRequestSerializer
from arkav.arkavauth.views.openapi.user import password_change_responses
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class PasswordChangeView(GenericAPIView):
    serializer_class = PasswordChangeRequestSerializer
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(responses=password_change_responses, operation_summary='Password Change')
    def post(self, request):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        password = request_serializer.validated_data['password']
        new_password = request_serializer.validated_data['new_password']

        if not request.user.check_password(password):
            return Response(
                {
                    'code': K_PASSWORD_CHANGE_FAILED,
                    'detail': 'Wrong old password.',
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.user.set_password(new_password)
        request.user.save()

        return Response({
            'code': K_PASSWORD_CHANGE_SUCCESSFUL,
            'detail': 'Your password has been changed.'
        })


class EditUserView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(operation_summary='Edit User')
    def patch(self, request):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)
