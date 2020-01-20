from django.contrib import admin
from django.utils.html import format_html
from arkav.eventcheckin.models import CheckInAttendance


class CheckInAttendanceInline(admin.TabularInline):
    model = CheckInAttendance
    extra = 0
