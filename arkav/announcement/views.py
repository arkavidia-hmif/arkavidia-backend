from arkav.announcement.models import AnnouncementUser
from arkav.announcement.serializers import AnnouncementUserSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class ListAnnouncementsView(generics.ListAPIView):
    serializer_class = AnnouncementUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        '''
        User should only be able to see his / her announcements
        '''
        return AnnouncementUser.objects.filter(user=self.request.user)
