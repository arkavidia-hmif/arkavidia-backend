from arkav.announcement.models import AnnouncementUser
from django.contrib import admin


@admin.register(AnnouncementUser)
class AnnouncementUserAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_sent')
    search_fields = ('title', )
    ordering = ('-date_sent',)
