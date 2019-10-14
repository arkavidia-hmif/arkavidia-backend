from arkav.competition.models import Competition
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from arkav.competition.serializers import CompetitionSerializer
from arkav.competition.serializers import RegisterTeamRequestSerializer
from arkav.competition.serializers import AddTeamMemberRequestSerializer
from arkav.competition.serializers import TeamSerializer
from arkav.competition.serializers import TeamDetailsSerializer
from arkav.competition.serializers import TeamMemberSerializer
from arkav.competition.serializers import TaskResponseSerializer
from arkav.competition.services import TaskResponseService
from arkav.competition.services import TeamService
from arkav.competition.services import TeamMemberService
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404
from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class ListCompetitionsView(generics.ListAPIView):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = (IsAuthenticated,)


class RegisterTeamView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None, *args, **kwargs):
        request_serializer = RegisterTeamRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        try:
            new_team = TeamService().create_team(request_serializer.validated_data, request.user)
            response_serializer = TeamSerializer(new_team)
            return Response(data=response_serializer.data)
        except SuspiciousOperation as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class AddTeamMemberView(views.APIView):
    permission_classes = (IsAuthenticated,)

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
        except SuspiciousOperation as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class ListTeamsView(generics.ListAPIView):
    serializer_class = TeamSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # User should only be able to see teams in which he/she is a member
        return Team.objects.filter(team_members__user=self.request.user)


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


class SubmitTaskResponseView(views.APIView):
    permission_classes = (IsAuthenticated,)

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
        except SuspiciousOperation as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
