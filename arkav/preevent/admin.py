from django.contrib import admin
from django.http import HttpResponseRedirect
from django.template.defaultfilters import escape
from django.template.response import TemplateResponse
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from arkav.preevent.admin_forms import AcceptTaskResponseActionForm
from arkav.preevent.admin_forms import RejectTaskResponseActionForm
from arkav.preevent.admin_inlines import StageInline
from arkav.preevent.admin_inlines import TaskInline
from arkav.preevent.admin_inlines import TaskResponseInline
from arkav.preevent.models import Preevent
from arkav.preevent.models import Stage
from arkav.preevent.models import Task
from arkav.preevent.models import TaskCategory
from arkav.preevent.models import TaskResponse
from arkav.preevent.models import TaskWidget
from arkav.preevent.models import Registrant


def send_reminder(modeladmin, request, queryset):
    for item in queryset:
        item.send_reminder()


send_reminder.short_description = 'Send reminder email'


@admin.register(Preevent)
class PreeventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'subtitle', 'is_registration_open']
    list_display_links = ['id', 'name']
    list_filter = ['is_registration_open']
    inlines = [StageInline]


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'preevent', 'order']
    list_display_links = ['id', 'name']
    list_filter = ['preevent']
    search_fields = ['name']
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'stage', 'category', 'widget', 'requires_validation']
    list_display_links = ['id', 'name']
    list_filter = ['category', 'widget', 'stage__preevent', 'stage']
    search_fields = ['name']


@admin.register(TaskResponse)
class TaskResponseAdmin(admin.ModelAdmin):
    list_display = ['registrant_link', 'task', 'status', 'open_response', 'accept_reject']
    list_display_links = ['task']
    list_filter = ['status', 'task__category']
    search_fields = ['registrant', 'task']
    autocomplete_fields = ['registrant', 'task']

    def registrant_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>'.format(reverse('admin:preevent_registrant_change',
                                                 args=(obj.registrant.id,)),
                                         escape(obj.registrant))
        )

    registrant_link.short_description = 'Registrant'

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
                name='preevent-{}-accept'.format(model_name),
            ),
            path(
                '<int:task_response_id>/reject/',
                self.admin_site.admin_view(self.reject_task_response),
                name='preevent-{}-reject'.format(model_name),
            ),
        ]
        return custom_urls + urls

    def accept_reject(self, obj):
        model_name = self.model._meta.model_name
        return format_html(
            '<a class="button" href="{}">Accept</a>&nbsp;'
            '<a class="button" href="{}">Reject</a>',
            reverse('admin:preevent-{}-accept'.format(model_name), args=[obj.pk]),
            reverse('admin:preevent-{}-reject'.format(model_name), args=[obj.pk]),
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
                    'admin:preevent_taskresponse_changelist',
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(url)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['task_response'] = task_response
        context['title'] = action_title

        return TemplateResponse(request, 'admin_task_response.html', context)


@admin.register(Registrant)
class RegistrantAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None, {"fields": ['user', 'preevent', 'active_stage']}
        ),
    )
    actions = [send_reminder]
    list_display = ['id', 'preevent', 'user', 'active_stage', 'has_completed_active_stage',
                    'is_participating', 'created_at']
    list_display_links = ['id', 'user']
    list_filter = ['is_participating', 'preevent', 'active_stage']
    search_fields = ['user']
    readonly_fields = ['full_name', 'current_education', 'institution', 'phone_number', 'address', 'birth_date']
    inlines = [TaskResponseInline]

    def has_completed_active_stage(self, instance):
        return instance.has_completed_active_stage
    has_completed_active_stage.boolean = True

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(RegistrantAdmin, self).get_fieldsets(request, obj)
        newfieldsets = list(fieldsets)
        fields = self.readonly_fields
        newfieldsets.append(['USER DATA', {'fields': fields}])
        return newfieldsets


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
