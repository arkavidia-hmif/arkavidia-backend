from arkav.competition.views import AddTeamMemberView
from arkav.competition.views import ListAnnouncementsView
from arkav.competition.views import ListCompetitionsView
from arkav.competition.views import ListTeamsView
from arkav.competition.views import RegisterTeamView
from arkav.competition.views import RetrieveUpdateDestroyTeamMemberView
from arkav.competition.views import RetrieveUpdateDestroyTeamView
from arkav.competition.views import SubmitTaskResponseView
from django.urls import path


urlpatterns = [
    path('', ListCompetitionsView.as_view(), name='competition-list'),
    path('register-team/', RegisterTeamView.as_view(), name='competition-team-register'),
    path('teams/', ListTeamsView.as_view(), name='competition-team-list'),
    path('teams/<int:team_id>/', RetrieveUpdateDestroyTeamView.as_view(), name='competition-team-detail'),
    path('teams/<int:team_id>/members/', AddTeamMemberView.as_view(), name='competition-team-member-list'),
    path('teams/<int:team_id>/members/<int:team_member_id>/',
         RetrieveUpdateDestroyTeamMemberView.as_view(), name='competition-team-member-detail'),
    path('teams/<int:team_id>/tasks/<int:task_id>/',
         SubmitTaskResponseView.as_view(), name='competition-team-task-detail'),
    path('announcements/', ListAnnouncementsView, name='competition-announcements'),
]
