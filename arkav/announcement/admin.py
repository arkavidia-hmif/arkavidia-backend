from arkav.announcement.models import Announcement
from django.contrib import admin


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_sent')
    search_fields = ('title', )
    ordering = ('-date_sent',)
