from arkav.arkavauth.models import User
from arkav.competition.models import Competition
from arkav.competition.serializers import CompetitionSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CompetitionTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1')

        self.competition_cp = Competition.objects.create(name='Competitive Programming')
        self.competition_ctf = Competition.objects.create(name='Capture the Flag', max_team_members=3)
        self.competition_without_stages = Competition.objects.create(name='Empty')

    def test_list_competition(self):
        '''
        List of competitions will be returned
        '''
        url = reverse('competition-list')
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res_competitions = res.data
        self.assertEqual(len(res_competitions), Competition.objects.count())
        for res_competition in res_competitions:
            competition = Competition.objects.get(id=res_competition['id'])
            self.assertDictEqual(res_competition, CompetitionSerializer(competition).data)

    def test_list_competition_unauthorized(self):
        '''
        If the user hasnt logged in, the result will be 403
        '''
        url = reverse('competition-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
