from arkav.competition.models import TaskResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone


class TeamService:

    def send_reminder_email(self, team):
        need_to_notify = []
        for task in team.active_stage.tasks.all():
            task_response_count = team.task_responses.filter(
                task__stage=team.active_stage,
                status__in=[TaskResponse.COMPLETED, TaskResponse.AWAITING_VALIDATION],
                task__id=task.id).count()
            if(not task_response_count):
                need_to_notify.append(task)

        addresses = []
        for member in team.members.all():
            addresses.append(member.email)

        context = {
            'team_name': team.name,
            'active_stage': team.active_stage,
            'tasks': need_to_notify,
        }
        text_template = get_template('team_reminder_email.txt')
        html_template = get_template('team_reminder_email.html')
        mail_text_message = text_template.render(context)
        mail_html_message = html_template.render(context)

        mail = EmailMultiAlternatives(
            subject='Reminder Lomba Arkavidia 5.0',
            body=mail_text_message,
            to=addresses
        )
        mail.attach_alternative(mail_html_message, 'text/html')
        mail.send()


class TeamMemberService:

    def send_invitation_email(self, team_member):
        context = {
            'team': team_member.team,
            'full_name': team_member.invitation_full_name,
        }
        text_template = get_template('team_invitation_confirmation_email.txt')
        html_template = get_template('team_invitation_confirmation_email.html')
        mail_text_message = text_template.render(context)
        mail_html_message = html_template.render(context)

        mail = EmailMultiAlternatives(
            subject='Pendaftaran Tim Arkavidia 5.0',
            body=mail_text_message,
            to=[team_member.invitation_email]
        )
        mail.attach_alternative(mail_html_message, 'text/html')
        mail.send()
        team_member.save()
