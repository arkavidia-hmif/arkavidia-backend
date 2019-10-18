from rest_framework import serializers
from arkav.announcement.models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Announcement
        fields = ('message', 'date_sent')
        read_only_fields = ('message', 'date_sent')
