from arkav.arkavauth.models import User
from arkav.competition.models import Competition
from arkav.competition.models import Stage
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegisterTeamTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1')

        self.competition_open = Competition.objects.create(name='Open Competition')
        self.competition_closed = Competition.objects.create(name='Closed Competition', is_registration_open=False)
        Stage.objects.create(competition=self.competition_open, name='Open Competition Stage')
        Stage.objects.create(competition=self.competition_closed, name='Closed Competition Stage')
        self.team_name = 'Team Name'
        self.team_institution = 'Team Institution'

    def test_register_team(self):
        '''
        Creates a team and team member objects by registering a team
        '''
        url = reverse('competition-team-register')
        self.client.force_authenticate(self.user1)

        data = {
            'competition_id': self.competition_open.pk,
            'name': self.team_name,
            'institution': self.team_institution,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Team.objects.count(), 1)

        team1 = Team.objects.first()
        self.assertEqual(team1.name, self.team_name)
        self.assertEqual(team1.team_members.count(), 1)
        self.assertEqual(team1.team_members.first().user.email, self.user1.email)

    def test_register_team_unauthorized(self):
        '''
        If user isn't logged in, returns 401
        '''
        url = reverse('competition-team-register')

        data = {
            'competition_id': self.competition_open.pk,
            'name': self.team_name,
            'institution': self.team_institution,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_team_already_registered(self):
        '''
        If user is already registered to the competition, returns 400
        '''
        url = reverse('competition-team-register')
        self.client.force_authenticate(self.user1)

        # Creates new team to the competition
        new_team = Team.objects.create(
            competition=self.competition_open,
            name=self.team_name,
            institution=self.team_institution,
            team_leader=self.user1,
        )

        # Add the current user as team member
        TeamMember.objects.create(
            team=new_team,
            user=self.user1,
            invitation_full_name=self.user1.full_name,
            invitation_email=self.user1.email,
        )

        data = {
            'competition_id': self.competition_open.pk,
            'name': self.team_name,
            'institution': self.team_institution,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_team_registration_closed(self):
        '''
        If the competition registration is already closed, returns 400
        '''
        url = reverse('competition-team-register')
        self.client.force_authenticate(self.user1)

        data = {
            'competition_id': self.competition_closed.pk,
            'name': self.team_name,
            'institution': self.team_institution,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_team_already_lead_other_team(self):
        '''
        If user has already lead other team, it will return 400
        '''
        url = reverse('competition-team-register')
        self.client.force_authenticate(self.user1)

        Team.objects.create(
            competition=self.competition_closed,
            name='abc',
            institution='ABC',
            team_leader=self.user1,
        )

        data = {
            'competition_id': self.competition_open.pk,
            'name': self.team_name,
            'institution': self.team_institution,
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
