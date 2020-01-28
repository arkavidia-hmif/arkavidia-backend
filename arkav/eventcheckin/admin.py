from arkav.eventcheckin.admin_inlines import CheckInAttendanceInline
from arkav.eventcheckin.models import CheckInEvent
from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.models import CheckInAttendee
from arkav.eventcheckin.services import CheckInService
from django.contrib import admin


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
    actions = ['send_qr_code']
    list_display = ('attendee', 'event', 'checkin_time', 'last_sent_token', )
    list_filter = ['event', 'checkin_time', 'last_sent_token']
    search_fields = ('attendee', 'event', )
    ordering = ('-checkin_time',)

    def send_qr_code(self, request, queryset):
        for obj in queryset:
            CheckInService().send_token_qr_code(obj)
        self.message_user(request,
                          'Check-In QR Codes are queued to be sent to {} attendances.'
                          .format(queryset.count()))
    send_qr_code.short_description = 'Send Check-In QR Code'
