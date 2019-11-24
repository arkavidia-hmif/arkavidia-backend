from arkav.announcement.models import Announcement
from arkav.announcement.models import AnnouncementUser
from django.contrib import admin


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', )
    search_fields = ('title', )


@admin.register(AnnouncementUser)
class AnnouncementUserAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'date_sent')
    search_fields = ('title', )
    ordering = ('-date_sent',)
