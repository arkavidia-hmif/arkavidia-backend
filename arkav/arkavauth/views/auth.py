from arkav.arkavauth.serializers import LoginRequestSerializer
from arkav.arkavauth.views.openapi.auth import login_responses
from arkav.utils.exceptions import ArkavAPIException
from arkav.utils.permissions import IsNotAuthenticated
from django.contrib.auth import logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.exceptions import TokenError


class LoginView(TokenObtainPairView):
    permission_classes = (IsNotAuthenticated, )
    serializer_class = LoginRequestSerializer

    @swagger_auto_schema(responses=login_responses, operation_summary='Login')
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        except ArkavAPIException as e:
            return e.as_response()

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        return None

    @swagger_auto_schema(operation_summary='Logout')
    @method_decorator(ensure_csrf_cookie)
    def post(self, request):
        logout(request)
        return Response()
