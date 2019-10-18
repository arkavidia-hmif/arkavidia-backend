from arkav.announcement.models import Announcement
from arkav.announcement.serializers import AnnouncementSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class ListAnnouncementsView(generics.ListAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        '''
        User should only be able to see his / her announcements
        '''
        return Announcement.objects.filter(user=self.request.user)
