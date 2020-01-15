from arkav.eventcheckin.models import CheckInEvent
from arkav.eventcheckin.models import CheckInAttendee
from django.contrib import admin


@admin.register(CheckInEvent)
class CheckInEventAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


@admin.register(CheckInAttendee)
class CheckInAttendeeAdmin(admin.ModelAdmin):
    actions = ['send_custom_email']
    list_display = ('name', 'email', 'checkin_time')
    list_filter = ['checkin_time']
    search_fields = ('name', 'email', )
    ordering = ('-checkin_time',)
