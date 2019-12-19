from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import Registrant
from arkav.mainevent.serializers import MaineventSerializer
from arkav.mainevent.serializers import MaineventDetailsSerializer
from arkav.mainevent.serializers import RegisterRegistrantRequestSerializer
from arkav.mainevent.serializers import RegistrantSerializer
from arkav.mainevent.serializers import RegistrantDetailsSerializer
from arkav.mainevent.serializers import TaskResponseSerializer
from arkav.mainevent.services import TaskResponseService
from arkav.mainevent.services import RegistrantService
from arkav.utils.exceptions import ArkavAPIException
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ListMaineventsView(generics.ListAPIView):
    queryset = Mainevent.objects.all()
    serializer_class = MaineventSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Mainevent List')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class DetailMaineventView(generics.ListAPIView):
    queryset = Mainevent.objects.all()
    serializer_class = MaineventDetailsSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Mainevent Detail')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RegisterRegistrantView(views.APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Registrant Registration',
                         request_body=RegisterRegistrantRequestSerializer,
                         responses={200: RegistrantSerializer()})
    def post(self, request, format=None, *args, **kwargs):
        request_serializer = RegisterRegistrantRequestSerializer(data=request.data)
        try:
            request_serializer.is_valid(raise_exception=True)
            new_registrant = RegistrantService().create_registrant(request_serializer.validated_data, request.user)
            response_serializer = RegistrantSerializer(new_registrant)
            return Response(data=response_serializer.data)
        except ArkavAPIException as e:
            return e.as_response()


class ListRegistrantsView(generics.ListAPIView):
    serializer_class = RegistrantSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # User should only be able to his/her own registration
        return Registrant.objects.filter(user=self.request.user)

    @swagger_auto_schema(operation_summary='Registrant List')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RetrieveUpdateDestroyRegistrantView(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'registrant_id'
    serializer_class = RegistrantDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # User should only be able to his/her own registration
        # Disable edit/delete if mainevent's is_registration_open is false or the registrant's is_participating is false
        if self.request.method == 'GET':
            return self.request.user.mainevent_registrants.all()
        else:
            return self.request.user.mainevent_registrants.filter(mainevent__is_registration_open=True,
                                                                  is_participating=True)

    def retrieve(self, request, *args, **kwargs):
        registrant = self.get_object()
        serializer = self.get_serializer(registrant)

        return Response(serializer.data)

    @swagger_auto_schema(operation_summary='Registrant Detail')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Registrant Update (Patch)')
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Registrant Update (Put)')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Registrant Delete')
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SubmitTaskResponseView(views.APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Submit Task Response',
                         request_body=TaskResponseSerializer,
                         responses={200: TaskResponseSerializer()})
    def post(self, request, format=None, *args, **kwargs):
        request_serializer = TaskResponseSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        try:
            task_response_status = TaskResponseService().submit_task_response(
                request_serializer.validated_data,
                registrant_id=self.kwargs['registrant_id'],
                task_id=self.kwargs['task_id'],
                user=request.user,
            )
            response_serializer = TaskResponseSerializer(task_response_status)
            return Response(data=response_serializer.data)
        except ArkavAPIException as e:
            return e.as_response()
