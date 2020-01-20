from arkav.eventcheckin.models import CheckInAttendee
from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.models import CheckInEvent
from rest_framework import serializers


class CheckInAttendeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckInAttendee
        fields = ('name', 'email', )


class CheckInEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = CheckInEvent
        fields = ('name', )


class CheckInRequestSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class CheckInResponseSerializer(serializers.ModelSerializer):
    attendee = CheckInAttendeeSerializer(read_only=True)
    event = CheckInEventSerializer(read_only=True)

    class Meta:
        model = CheckInAttendance
        fields = ('attendee', 'event', 'checkin_time')
        read_only_fields = ('attendee', 'event', 'token', 'checkin_time')
