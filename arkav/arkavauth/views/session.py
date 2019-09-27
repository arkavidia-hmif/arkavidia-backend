from arkav.arkavauth.serializers import UserSerializer
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def get_current_session_view(request):
    response_serializer = UserSerializer(request.user)
    return Response(data=response_serializer.data)
