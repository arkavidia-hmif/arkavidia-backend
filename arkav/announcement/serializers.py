from rest_framework import serializers
from arkav.announcement.models import AnnouncementUser


class AnnouncementUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnnouncementUser
        fields = ('title', 'message', 'date_sent')
        read_only_fields = ('title', 'message', 'date_sent')
