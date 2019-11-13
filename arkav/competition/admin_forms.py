from django import forms
from arkav.competition.models import TaskResponse
from arkav.competition.services import TaskResponseService


class RejectTaskResponseActionForm(forms.Form):
    reason = forms.CharField(required=True, widget=forms.Textarea)
    field_order = ('reason',)

    def save(self, task_response, user):
        TaskResponseService().reject_task_response(task_response, self.cleaned_data['reason'])


class AcceptTaskResponseActionForm(forms.Form):

    def save(self, task_response, user):
        TaskResponseService().accept_task_response(task_response)
