from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from arkav.competition.models import Stage
from arkav.competition.models import Task
from arkav.competition.models import TaskResponse
from arkav.competition.models import TeamMember
from arkav.competition.services import TeamMemberService
import re


def resend_invitation_email(modeladmin, request, queryset):
    for obj in queryset:
        TeamMemberService().send_invitation_email(obj)


resend_invitation_email.short_description = 'Resend the invitation email of the selected members with the same token.'


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
    fields = ['team', 'task', 'status', 'file_link', 'last_submitted_at']
    readonly_fields = ['file_link', 'last_submitted_at']
    autocomplete_fields = ['team', 'task']
    extra = 1

    def file_link(self, obj):
        response, is_link = obj.response_or_link
        if is_link:
            return format_html('<a href="{}">Open</a>'.format(response))
        return response

    file_link.short_descripton = 'Link / Answer'


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    fields = [
        'user', 'has_user_account', 'is_leader',
        'invitation_full_name', 'invitation_email', 'created_at'
    ]
    readonly_fields = ['has_user_account', 'is_leader', 'created_at']
    actions = [resend_invitation_email]
    extra = 1

    def has_user_account(self, obj):
        return obj.has_account
    has_user_account.boolean = True

    def is_leader(self, obj):
        return obj.is_team_leader
    is_leader.boolean = True
