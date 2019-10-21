from arkav.arkavauth.constants import K_LOGIN_FAILED
from arkav.arkavauth.constants import K_ACCOUNT_EMAIL_NOT_CONFIRMED
from arkav.arkavauth.serializers import UserSerializer
from arkav.arkavauth.serializers import LoginRequestSerializer
from arkav.arkavauth.views.openapi.auth import login_responses
from arkav.utils.permissions import IsNotAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class LoginView(GenericAPIView):
    serializer_class = LoginRequestSerializer
    permission_classes = (IsNotAuthenticated, )

    @swagger_auto_schema(responses=login_responses, operation_summary='Login')
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, format=None):
        request_serializer = self.serializer_class(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        user = authenticate(
            email=request_serializer.validated_data['email'].lower(),
            password=request_serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {
                    'code': K_LOGIN_FAILED,
                    'detail': 'Wrong email or password.',
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_email_confirmed:
            return Response(
                {
                    'code': K_ACCOUNT_EMAIL_NOT_CONFIRMED,
                    'detail': 'Account email hasn\'t been confirmed. Check inbox for confirmation email.',
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        response_serializer = UserSerializer(request.user)
        return Response(data=response_serializer.data)


class LogoutView(GenericAPIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(operation_summary='Logout')
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        logout(request)
        return Response()
