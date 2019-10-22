from arkav.arkavauth.models import User
from arkav.competition.models import Competition
from arkav.competition.models import Stage
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AddTeamMemberTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1')
        self.competition_open = Competition.objects.create(name='Open Competition', max_team_members=100)
        Stage.objects.create(competition=self.competition_open, name='Open Competition Stage')

        self.team1 = Team.objects.create(
            competition=self.competition_open,
            name='Team Name',
            institution='Team Institution',
            team_leader=self.user1
        )

        TeamMember.objects.create(
            team=self.team1,
            user=self.user1,
            invitation_full_name=self.user1.full_name,
            invitation_email=self.user1.email,
        )

        self.full_name = 'Full Name'
        self.email = 'email@example.org'

    def test_add_team_member_with_no_account(self):
        '''
        Adds new member with no account to the team whose one of the members is user
        '''
        url = reverse('competition-team-member-list', kwargs={'team_id': self.team1.pk})
        self.client.force_authenticate(self.user1)

        data = {
            'full_name': self.full_name,
            'email': self.email
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(self.team1.team_members.count(), 2)
        self.assertEqual(self.team1.team_members.filter(invitation_full_name=self.full_name).exists(), True)
        self.assertEqual(self.team1.team_members.get(invitation_full_name=self.full_name).has_account, False)

    def test_add_team_member_with_account(self):
        '''
        Adds new member with existing account to the team whose one of the members is user
        '''
        url = reverse('competition-team-member-list', kwargs={'team_id': self.team1.pk})
        self.client.force_authenticate(self.user1)

        User.objects.create_user(full_name=self.full_name, email=self.email)
        data = {
            'full_name': self.full_name,
            'email': self.email
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(self.team1.team_members.count(), 2)
        self.assertEqual(self.team1.team_members.filter(user__full_name=self.full_name).exists(), True)
        self.assertEqual(self.team1.team_members.get(user__full_name=self.full_name).has_account, True)

    def test_add_team_member_unauthorized(self):
        '''
        If user isn't logged in, returns 401
        '''
        url = reverse('competition-team-member-list', kwargs={'team_id': self.team1.pk})

        data = {
            'full_name': self.full_name,
            'email': self.email
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_team_member_registration_closed(self):
        '''
        If the competition registration is already closed, returns 400
        '''
        url = reverse('competition-team-member-list', kwargs={'team_id': self.team1.pk})
        self.client.force_authenticate(self.user1)

        self.team1.competition = Competition.objects.create(
            name='Closed Competition', is_registration_open=False, max_team_members=100)
        self.team1.save()
        data = {
            'full_name': self.full_name,
            'email': self.email
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['code'], 'competition_registration_closed')

    def test_add_team_member_not_participating(self):
        '''
        If the team is not participating anymore, returns 400
        '''
        url = reverse('competition-team-member-list', kwargs={'team_id': self.team1.pk})
        self.client.force_authenticate(self.user1)

        self.team1.is_participating = False
        self.team1.save()
        data = {
            'full_name': self.full_name,
            'email': self.email
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['code'], 'team_not_participating')

    def test_add_team_member_full(self):
        '''
        If the team has reached competition member count limit, returns 400
        '''
        url = reverse('competition-team-member-list', kwargs={'team_id': self.team1.pk})
        self.client.force_authenticate(self.user1)

        self.team1.competition = Competition.objects.create(
            name='One-Man Competition', max_team_members=1)
        self.team1.save()
        data = {
            'full_name': self.full_name,
            'email': self.email
        }

        res = self.client.post(url, data=data, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data['code'], 'team_full')
