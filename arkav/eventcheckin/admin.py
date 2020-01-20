from arkav.eventcheckin.admin_inlines import CheckInAttendanceInline
from arkav.eventcheckin.models import CheckInEvent
from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.models import CheckInAttendee
from django import forms
from django.contrib import admin
from django.contrib.admin.helpers import ActionForm


@admin.register(CheckInEvent)
class CheckInEventAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    inlines = [CheckInAttendanceInline]


@admin.register(CheckInAttendee)
class CheckInAttendeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', )
    search_fields = ('name', 'email', )
    inlines = [CheckInAttendanceInline]


@admin.register(CheckInAttendance)
class CheckInAttendanceAdmin(admin.ModelAdmin):
    list_display = ('attendee', 'event', 'checkin_time', )
    list_filter = ['event', 'checkin_time']
    search_fields = ('attendee', 'event', )
    ordering = ('-checkin_time',)
