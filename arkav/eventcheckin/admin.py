from arkav.eventcheckin.admin_inlines import CheckInAttendanceInline
from arkav.eventcheckin.models import CheckInEvent
from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.models import CheckInAttendee
from arkav.eventcheckin.services import CheckInService
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render


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
    actions = ['send_templated_email']
    list_display = ('attendee', 'event', 'last_sent_token', 'pax', 'pax_checked_in')
    list_filter = ['event']
    search_fields = ('attendee', 'event', 'token')
    ordering = ('-last_sent_token',)

    def send_templated_email(self, request, queryset):
        if 'apply' in request.POST:
            for obj in queryset:
                CheckInService().send_templated_email(
                    obj,
                    request.POST['subject_template'],
                    request.POST['text_template'],
                    request.POST['html_template'],
                )
            self.message_user(request,
                              'Rendered check-in emails queued to be sent to {} attendances.'
                              .format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())

        subject_template = '[Arkavidia] {{ event.name }} - Check-In QR Code'
        with open('arkav/eventcheckin/templates/token_qr_code_email.txt') as f_text_template:
            text_template = f_text_template.read()
        with open('arkav/eventcheckin/templates/token_qr_code_email.html') as f_html_template:
            html_template = f_html_template.read()
        return render(request,
                      'eventcheckin_admin_custom_email.html',
                      context={
                          'attendances': queryset,
                          'subject_template': subject_template,
                          'text_template': text_template,
                          'html_template': html_template,
                      })
    send_templated_email.short_description = 'Send Templated Check-In Email'
