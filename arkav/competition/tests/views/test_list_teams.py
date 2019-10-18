from arkav.arkavauth.models import User
from arkav.competition.models import Competition
from arkav.competition.models import Stage
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from arkav.competition.serializers import TeamSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ListTeamsTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user')

        for i in range(5):
            competition = Competition.objects.create(name='Competition {}'.format(i))
            Stage.objects.create(competition=competition, name='Stage {}'.format(i))

            TeamMember.objects.create(
                team=Team.objects.create(
                    competition=competition,
                    name='Team {}'.format(i),
                    institution='Team Institution',
                    team_leader=User.objects.create_user(email='user{}'.format(i))
                ),
                user=self.user1,
                invitation_full_name=self.user1.full_name,
                invitation_email=self.user1.email,
            )

    def test_list_teams(self):
        '''
        List of teams will be returned
        '''
        url = reverse('competition-team-list')
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res_teams = res.data
        self.assertEqual(len(res_teams), Team.objects.count())
        for res_team in res_teams:
            team = Team.objects.get(id=res_team['id'])
            self.assertDictEqual(res_team, TeamSerializer(team).data)

    def test_list_teams_unauthorized(self):
        '''
        If the user isn't logged in, returns 403
        '''
        url = reverse('competition-team-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
