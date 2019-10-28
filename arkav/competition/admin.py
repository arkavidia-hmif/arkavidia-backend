from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from arkav.competition.admin_forms import AcceptTaskResponseActionForm
from arkav.competition.admin_forms import RejectTaskResponseActionForm
from arkav.competition.admin_inlines import StageInline
from arkav.competition.admin_inlines import TaskInline
from arkav.competition.admin_inlines import TeamMemberInline
from arkav.competition.admin_inlines import TaskResponseInline
from arkav.competition.models import Competition
from arkav.competition.models import Stage
from arkav.competition.models import Task
from arkav.competition.models import TaskCategory
from arkav.competition.models import TaskResponse
from arkav.competition.models import TaskWidget
from arkav.competition.models import Team


def send_reminder(modeladmin, request, queryset):
    for item in queryset:
        item.send_reminder()


send_reminder.short_description = 'Send reminder email'


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'min_team_members', 'max_team_members', 'is_registration_open']
    list_display_links = ['id', 'name']
    list_filter = ['is_registration_open']
    inlines = [StageInline]


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
    list_display = ['team', 'task', 'status', 'open_response', 'accept_reject']
    list_display_links = ['team']
    list_filter = ['status', 'task__category']
    search_fields = ['team', 'task']
    autocomplete_fields = ['team', 'task']

    def open_response(self, obj):
        response, is_link = obj.response_or_link
        if is_link:
            return format_html('<a href="{}">Open</a>'.format(response))
        return response

    open_response.short_description = 'Content'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:task_response_id>/accept/',
                self.admin_site.admin_view(self.accept_task_response),
                name='competition-taskresponse-accept',
            ),
            path(
                '<int:task_response_id>/reject/',
                self.admin_site.admin_view(self.reject_task_response),
                name='competition-taskresponse-reject',
            ),
        ]
        return custom_urls + urls

    def accept_reject(self, obj):
        return format_html(
            '<a class="button" href="{}">Accept</a>&nbsp;'
            '<a class="button" href="{}">Reject</a>',
            reverse('admin:competition-taskresponse-accept', args=[obj.pk]),
            reverse('admin:competition-taskresponse-reject', args=[obj.pk]),
        )

    accept_reject.short_description = 'Accept / Reject'
    accept_reject.allow_tags = True

    def accept_task_response(self, request, task_response_id, *args, **kwargs):
        return self.process_task_response(
            request=request,
            task_response_id=task_response_id,
            action_form=AcceptTaskResponseActionForm,
            action_title='Accept',
        )

    def reject_task_response(self, request, task_response_id, *args, **kwargs):
        return self.process_task_response(
            request=request,
            task_response_id=task_response_id,
            action_form=RejectTaskResponseActionForm,
            action_title='Reject',
        )

    def process_task_response(self, request, task_response_id, action_form, action_title):
        task_response = self.get_object(request, task_response_id)

        if request.method != 'POST':
            form = action_form()
        else:
            form = action_form(request.POST)
            if form.is_valid():
                form.save(task_response, request.user)
                self.message_user(request, 'Success')
                url = reverse(
                    'admin:competition_taskresponse_changelist',
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(url)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['task_response'] = task_response
        context['title'] = action_title

        return TemplateResponse(request, 'admin_task_response.html', context)


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
