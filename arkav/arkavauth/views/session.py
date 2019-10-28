from arkav.arkavauth.serializers import UserSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class SessionView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(operation_summary='Session')
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, format=None):
        response_serializer = self.serializer_class(request.user)
        return Response(data=response_serializer.data)
