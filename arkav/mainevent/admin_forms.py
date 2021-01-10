from django import forms
from arkav.mainevent.models import TaskResponse


class RejectTaskResponseActionForm(forms.Form):
    reason = forms.CharField(required=True, widget=forms.Textarea)
    field_order = ('reason',)

    def save(self, task_response, user):
        task_response.reason = self.cleaned_data['reason']
        task_response.status = TaskResponse.REJECTED
        task_response.save()


class AcceptTaskResponseActionForm(forms.Form):

    def save(self, task_response, user):
        task_response.reason = ''
        task_response.status = TaskResponse.COMPLETED
        task_response.save()

        registrant = task_response.registrant
        if registrant.has_completed_active_stage:
            registrant.is_participating = True
            registrant.save()
            registrant.mainevent.update_seats_remaining()
