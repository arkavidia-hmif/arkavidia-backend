from django.contrib import admin
from django.utils.html import format_html
from arkav.preevent.models import Stage
from arkav.preevent.models import Task
from arkav.preevent.models import TaskResponse


class StageInline(admin.TabularInline):
    model = Stage
    fields = ['name', 'order']
    extra = 1
    show_change_link = True


class TaskInline(admin.TabularInline):
    model = Task
    fields = ['name', 'stage', 'category', 'widget', 'requires_validation']
    extra = 1
    show_change_link = True


class TaskResponseInline(admin.TabularInline):
    model = TaskResponse
    fields = ['registrant', 'task', 'status', 'file_link', 'last_submitted_at']
    readonly_fields = ['file_link', 'last_submitted_at']
    autocomplete_fields = ['registrant', 'task']
    extra = 1

    def file_link(self, obj):
        response, is_link = obj.response_or_link
        if is_link:
            return format_html('<a href="{}">Open</a>'.format(response))
        return response

    file_link.short_descripton = 'Link / Answer'
