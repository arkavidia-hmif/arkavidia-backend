from arkav.arkavauth.models import User
from arkav.competition.models import Competition
from arkav.competition.serializers import CompetitionSerializer
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CompetitionListTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email='user1', current_education='SMA')
        self.user2 = User.objects.create_user(email='user2', current_education='Mahasiswa')

        self.competition_cp = Competition.objects.create(name='Competitive Programming', education_level='SMA')
        self.competition_cp_mhs = Competition.objects.create(name='Competitive Programming', education_level='Mahasiswa')
        self.competition_ctf = Competition.objects.create(name='Capture the Flag', education_level='SMA', max_team_members=3)
        self.competition_without_stages = Competition.objects.create(name='Empty', education_level='SMA')

    def test_list_competitions(self):
        '''
        List of competitions will be returned only for their equal education level
        '''
        url = reverse('competition-list')
        self.client.force_authenticate(self.user1)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res_competitions = res.data
        self.assertEqual(len(res_competitions), Competition.objects.filter(education_level='SMA').count())
        for res_competition in res_competitions:
            competition = Competition.objects.get(id=res_competition['id'])
            self.assertDictEqual(res_competition, CompetitionSerializer(competition).data)

    def test_list_competitions_unauthorized(self):
        '''
        If the user hasnt logged in, the result will be 401
        '''
        url = reverse('competition-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
