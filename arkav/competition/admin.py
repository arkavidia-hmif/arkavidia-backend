from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from arkav.competition.models import Competition
from arkav.competition.models import Stage
from arkav.competition.models import Task
from arkav.competition.models import TaskCategory
from arkav.competition.models import TaskResponse
from arkav.competition.models import TaskWidget
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from arkav.competition.services import TeamMemberService
import re


def send_reminder(adminModel, request, queryset):
    for item in queryset:
        item.send_reminder()


send_reminder.short_description = 'Send reminder email'


def resend_invitation_email(modeladmin, request, queryset):
    for obj in queryset:
        TeamMemberService().send_invitation_email(obj)


resend_invitation_email.short_description = 'Resend the invitation email of the selected members with the same token.'


class StageInline(admin.TabularInline):
    model = Stage
    fields = ['name', 'order']
    extra = 1
    show_change_link = True


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'min_team_members', 'max_team_members', 'is_registration_open']
    list_display_links = ['id', 'name']
    list_filter = ['is_registration_open']
    inlines = [StageInline]


class TaskInline(admin.TabularInline):
    model = Task
    fields = ['name', 'stage', 'category', 'widget', 'requires_validation']
    extra = 1
    show_change_link = True


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'competition', 'order']
    list_display_links = ['id', 'name']
    list_filter = ['competition']
    search_fields = ['name']
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'stage', 'category', 'widget', 'requires_validation']
    list_display_links = ['id', 'name']
    list_filter = ['category', 'widget', 'stage__competition', 'stage']
    search_fields = ['name']


@admin.register(TaskResponse)
class TaskResponseAdmin(admin.ModelAdmin):
    list_display = ['id', 'team', 'task', 'status', 'last_submitted_at']
    list_display_links = ['id']
    list_filter = ['status', 'task__category']
    search_fields = ['team', 'task']
    autocomplete_fields = ['team', 'task']


class TaskResponseInline(admin.TabularInline):
    model = TaskResponse
    fields = ['team', 'task', 'status', 'response', 'file_link', 'last_submitted_at']
    readonly_fields = ['file_link', 'last_submitted_at']
    autocomplete_fields = ['team', 'task']
    extra = 1

    def file_link(self, instance):
        uuidv4_regex = r'[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}'
        if re.match(uuidv4_regex, str(instance.response)) is not None:
            link = reverse('download', kwargs={'file_id': str(instance.response)})
            return format_html('<a href="{}">Open file</a>', link)
        else:
            return ''


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


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    actions = [send_reminder]
    list_display = ['id', 'name', 'competition', 'institution', 'team_leader',
                    'active_stage', 'has_completed_active_stage', 'is_participating', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['is_participating', 'institution', 'competition', 'active_stage']
    search_fields = ['name']
    autocomplete_fields = ['team_leader']
    inlines = [TeamMemberInline, TaskResponseInline]

    def has_completed_active_stage(self, instance):
        return instance.has_completed_active_stage
    has_completed_active_stage.boolean = True


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    search_fields = ['name']


@admin.register(TaskWidget)
class TaskWidgetAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']
    search_fields = ['name']
