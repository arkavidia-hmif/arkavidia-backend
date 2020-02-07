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
    password = serializers.CharField(max_length=100)


class CheckInResponseSerializer(serializers.ModelSerializer):
    attendee_name = serializers.SerializerMethodField()
    attendee_email = serializers.SerializerMethodField()
    event = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CheckInAttendance
        fields = ('attendee_name', 'attendee_email', 'event', 'pax', 'pax_checked_in')
        read_only_fields = ('attendee_name', 'attendee_email', 'event', 'token', 'pax', 'pax_checked_in')

    def get_attendee_name(self, obj):
        return obj.attendee.name

    def get_attendee_email(self, obj):
        return obj.attendee.email
