from django.contrib import admin
from arkav.eventcheckin.models import CheckInAttendance


class CheckInAttendanceInline(admin.TabularInline):
    model = CheckInAttendance
    extra = 0
