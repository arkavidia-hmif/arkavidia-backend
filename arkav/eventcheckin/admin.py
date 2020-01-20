from arkav.eventcheckin.models import CheckInEvent
from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.models import CheckInAttendee
from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm


class XForm(ActionForm):
    target_event = forms.ModelChoiceField(queryset=CheckInEvent.objects.all(), empty_label="(Nothing)")


def send_checkin_token(modeladmin, request, queryset):
    print('Dummy send token')


send_checkin_token.short_description = 'Send Check-in Token (QR Code)'


@admin.register(CheckInEvent)
class CheckInEventAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


@admin.register(CheckInAttendee)
class CheckInAttendeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', )
    search_fields = ('name', 'email', )


@admin.register(CheckInAttendance)
class CheckInAttendanceAdmin(admin.ModelAdmin):
    action_form = XForm
    actions = [send_checkin_token]
    list_display = ('attendee', 'event', 'checkin_time', )
    list_filter = ['event', 'checkin_time']
    search_fields = ('attendee', 'event', )
    ordering = ('-checkin_time',)
