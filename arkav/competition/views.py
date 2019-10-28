from arkav.competition.models import Competition
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from arkav.competition.serializers import AddTeamMemberRequestSerializer
from arkav.competition.serializers import CompetitionSerializer
from arkav.competition.serializers import RegisterTeamRequestSerializer
from arkav.competition.serializers import TeamSerializer
from arkav.competition.serializers import TeamDetailsSerializer
from arkav.competition.serializers import TeamMemberSerializer
from arkav.competition.serializers import TaskResponseSerializer
from arkav.competition.services import TaskResponseService
from arkav.competition.services import TeamService
from arkav.competition.services import TeamMemberService
from arkav.utils.exceptions import ArkavAPIException
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ListCompetitionsView(generics.ListAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Competition List')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RegisterTeamView(views.APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Team Registration',
                         request_body=RegisterTeamRequestSerializer,
                         responses={200: TeamSerializer()})
    def post(self, request, format=None, *args, **kwargs):
        request_serializer = RegisterTeamRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        try:
            new_team = TeamService().create_team(request_serializer.validated_data, request.user)
            response_serializer = TeamSerializer(new_team)
            return Response(data=response_serializer.data)
        except ArkavAPIException as e:
            return e.as_response()


class AddTeamMemberView(views.APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Add Team Member',
                         request_body=AddTeamMemberRequestSerializer,
                         responses={200: TeamMemberSerializer()})
    def post(self, request, format=None, *args, **kwargs):
        request_serializer = AddTeamMemberRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        try:
            new_team_member = TeamMemberService().create_team_member(
                request_serializer.validated_data,
                self.kwargs['team_id'],
                request.user
            )
            response_serializer = TeamMemberSerializer(new_team_member)
            return Response(data=response_serializer.data)
        except ArkavAPIException as e:
            return e.as_response()


class ListTeamsView(generics.ListAPIView):
    serializer_class = TeamSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # User should only be able to see teams in which he/she is a member
        return Team.objects.filter(team_members__user=self.request.user)

    @swagger_auto_schema(operation_summary='Team List')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class RetrieveUpdateDestroyTeamView(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'team_id'
    serializer_class = TeamDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # User should only be able to see teams in which he/she is a member
        # Disable edit/delete if competition's is_registration_open is false or the team's is_participating is false
        if self.request.method == 'GET':
            return self.request.user.teams.all()
        else:
            return self.request.user.teams.filter(competition__is_registration_open=True, is_participating=True)

    @swagger_auto_schema(operation_summary='Team Detail')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Team Update (Patch)')
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Team Update (Put)')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Team Delete')
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class RetrieveUpdateDestroyTeamMemberView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # User should only be able to see teams in which he/she is a member
        # Disable edit/delete if competition's is_registration_open is false or the team's is_participating is false
        if self.request.method == 'GET':
            return TeamMember.objects.filter(team__in=self.request.user.teams.all())
        else:
            return TeamMember.objects.filter(
                team__in=self.request.user.teams.all(),
                team__competition__is_registration_open=True,
                team__is_participating=True
            )

    def get_object(self):
        instance = get_object_or_404(
            self.get_queryset(),
            team__id=self.kwargs['team_id'],
            id=self.kwargs['team_member_id'],
        )
        self.check_object_permissions(self.request, instance)
        return instance

    @swagger_auto_schema(operation_summary='Team Member Detail')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Team Member Update (Patch)')
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Team Member Update (Put)')
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='Team Member Delete')
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
                team_id=self.kwargs['team_id'],
                task_id=self.kwargs['task_id'],
                user=request.user
            )
            response_serializer = TaskResponseSerializer(task_response_status)
            return Response(data=response_serializer.data)
        except ArkavAPIException as e:
            return e.as_response()
