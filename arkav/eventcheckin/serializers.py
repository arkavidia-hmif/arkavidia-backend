from arkav.eventcheckin.models import CheckInAttendee
from arkav.eventcheckin.models import CheckInEvent
from rest_framework import serializers


class CheckInEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckInEvent
        fields = ('name', )


class CheckInRequestSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class CheckInResponseSerializer(serializers.ModelSerializer):
    event = CheckInEventSerializer(read_only=True)

    class Meta:
        model = CheckInAttendee
        fields = ('name', 'email', 'event', 'checkin_time')
        read_only_fields = ('name', 'email', 'event', 'token', 'checkin_time')
