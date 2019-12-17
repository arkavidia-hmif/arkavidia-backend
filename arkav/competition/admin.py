from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.defaultfilters import escape
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
from arkav.competition.admin_inlines import UserTaskResponseInline
from arkav.competition.models import Competition
from arkav.competition.models import Stage
from arkav.competition.models import Task
from arkav.competition.models import TaskCategory
from arkav.competition.models import TaskResponse
from arkav.competition.models import UserTaskResponse
from arkav.competition.models import TaskWidget
from arkav.competition.models import Team
from arkav.competition.services import TeamService


def send_reminder(modeladmin, request, queryset):
    for item in queryset:
        TeamService().send_reminder_email(item)


send_reminder.short_description = 'Send reminder email'


def move_to_next_stage(modeladmin, request, queryset):
    for item in queryset:
        next_stage = Stage.objects.filter(
            competition=item.competition,
            order__gt=item.active_stage.order,
        ).order_by('order').first()
        item.active_stage = next_stage
        item.save()


move_to_next_stage.short_description = 'Move to next stage'


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
    list_display = ['id', 'name', 'stage', 'category', 'widget', 'requires_validation', 'is_user_task']
    list_display_links = ['id', 'name']
    list_filter = ['category', 'widget', 'stage__competition', 'stage']
    search_fields = ['name']


class AbstractTaskResponseAdmin(admin.ModelAdmin):
    list_display = ['team_link', 'task', 'status', 'open_response', 'accept_reject']
    list_display_links = ['task']
    list_filter = ['status', 'task__category']
    search_fields = ['team__name', 'team__id', 'task__name']
    autocomplete_fields = ['team', 'task']

    def team_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>'.format(reverse('admin:competition_team_change',
                                                 args=(obj.team.id,)),
                                         escape(obj.team))
        )

    team_link.short_description = 'Team'

    def open_response(self, obj):
        response, is_link = obj.response_or_link
        if is_link:
            return format_html('<a href="{}">Open</a>'.format(response))
        return response

    open_response.short_description = 'Content'

    def get_urls(self):
        urls = super().get_urls()
        model_name = self.model._meta.model_name
        custom_urls = [
            path(
                '<int:task_response_id>/accept/',
                self.admin_site.admin_view(self.accept_task_response),
                name='competition-{}-accept'.format(model_name),
            ),
            path(
                '<int:task_response_id>/reject/',
                self.admin_site.admin_view(self.reject_task_response),
                name='competition-{}-reject'.format(model_name),
            ),
        ]
        return custom_urls + urls

    def accept_reject(self, obj):
        model_name = self.model._meta.model_name
        return format_html(
            '<a class="button" href="{}">Accept</a>&nbsp;'
            '<a class="button" href="{}">Reject</a>',
            reverse('admin:competition-{}-accept'.format(model_name), args=[obj.pk]),
            reverse('admin:competition-{}-reject'.format(model_name), args=[obj.pk]),
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
                    'admin:competition_{}_changelist'.format(self.model._meta.model_name),
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(url)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['task_response'] = task_response
        context['title'] = action_title

        return TemplateResponse(request, 'admin_task_response.html', context)


@admin.register(TaskResponse)
class TaskResponseAdmin(AbstractTaskResponseAdmin):
    pass


@admin.register(UserTaskResponse)
class UserTaskResponseAdmin(AbstractTaskResponseAdmin):
    list_display = ['team_link', 'task', 'team_member_name', 'status', 'open_response', 'accept_reject']

    def team_member_name(self, obj):
        return obj.team_member.full_name

    team_member_name.short_description = 'Team Member'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    actions = [move_to_next_stage, 'send_custom_email', send_reminder]
    list_display = ['id', 'name', 'competition', 'institution', 'team_leader',
                    'active_stage', 'has_completed_active_stage', 'is_participating', 'created_at']
    list_display_links = ['id', 'name']
    list_filter = ['is_participating', 'institution', 'competition', 'active_stage']
    search_fields = ['name']
    autocomplete_fields = ['team_leader']
    inlines = [TeamMemberInline, TaskResponseInline, UserTaskResponseInline]

    def has_completed_active_stage(self, instance):
        return instance.has_completed_active_stage
    has_completed_active_stage.boolean = True

    def send_custom_email(self, request, queryset):
        if 'apply' in request.POST:
            TeamService().send_custom_email(
                queryset,
                request.POST['subject'],
                request.POST['mail_text_message'],
                request.POST['mail_html_message'],
            )
            self.message_user(request, 'Sent email to {} teams'.format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())

        return render(request, 'admin_custom_email.html', context={'teams': queryset})
    send_custom_email.short_description = 'Send Customized Email'


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
