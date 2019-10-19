from arkav.arkavauth.serializers import UserSerializer
from arkav.arkavauth.serializers import LoginRequestSerializer
from arkav.utils.permissions import IsNotAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class SessionView(GenericAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        response_serializer = UserSerializer(request.user)
        return Response(data=response_serializer.data)


class LoginView(GenericAPIView):
    serializer_class = LoginRequestSerializer
    permission_classes = (IsNotAuthenticated, )

    def post(self, request, format=None):
        request_serializer = LoginRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        user = authenticate(
            email=request_serializer.validated_data['email'].lower(),
            password=request_serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {
                    'code': 'login_failed',
                    'detail': 'Wrong email or password.',
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_email_confirmed:
            return Response(
                {
                    'code': 'account_email_not_confirmed',
                    'detail': 'Account email hasn\'t been confirmed. Check inbox for confirmation email.',
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        response_serializer = UserSerializer(request.user)
        return Response(data=response_serializer.data)


@ensure_csrf_cookie
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def logout_view(request):
    logout(request)
    return Response()
