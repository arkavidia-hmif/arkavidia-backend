
from arkav.eventcheckin.models import CheckInAttendance
from arkav.eventcheckin.models import CheckInAttendee
from arkav.announcement.services import AnnouncementService
from arkav.arkavauth.models import User
from arkav.competition.models import AbstractTaskResponse
from arkav.competition.models import Task
from arkav.competition.models import TaskResponse
from arkav.competition.models import Team
from arkav.competition.models import TeamMember
from arkav.competition.models import UserTaskResponse
from arkav.utils.exceptions import ArkavAPIException
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.utils import timezone
from rest_framework import status
import django_rq

from arkav.competition.constants import K_COMPETITION_REGISTRATION_CLOSED
from arkav.competition.constants import K_COMPETITION_REGISTRATION_CLOSED_DETAIL
from arkav.competition.constants import K_TEAM_NOT_PARTICIPATING
from arkav.competition.constants import K_TEAM_NOT_PARTICIPATING_DETAIL
from arkav.competition.constants import K_TEAM_HAS_SELECTED_MEMBER
from arkav.competition.constants import K_TEAM_HAS_SELECTED_MEMBER_DETAIL
from arkav.competition.constants import K_TEAM_FULL
from arkav.competition.constants import K_TEAM_FULL_DETAIL
from arkav.competition.constants import K_COMPETITION_ALREADY_REGISTERED
from arkav.competition.constants import K_COMPETITION_ALREADY_REGISTERED_DETAIL


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
        text_template = get_template('competition_team_reminder_email.txt')
        html_template = get_template('competition_team_reminder_email.html')
        mail_text_message = text_template.render(context)
        mail_html_message = html_template.render(context)

        mail = EmailMultiAlternatives(
            subject='Reminder Lomba Arkavidia 7.0',
            body=mail_text_message,
            to=addresses,
        )
        mail.attach_alternative(mail_html_message, 'text/html')
        mail.send()

    def send_custom_email(self, teams, subject, mail_text_message, mail_html_message):
        for team in teams.all():
            addresses = []
            for member in team.team_members.all():
                if (member.user):
                    addresses.append(member.user.email)
                else:
                    addresses.append(member.email)

            mail = EmailMultiAlternatives(
                subject=subject,
                body=mail_text_message,
                to=addresses,
            )
            mail.attach_alternative(mail_html_message, 'text/html')
            django_rq.enqueue(mail.send)

    @transaction.atomic
    def create_team(self, team_data, user):
        competition = team_data['competition_id']
        team_name = team_data['name']
        team_institution = team_data['institution']

        # Only register if registration is open for this competition
        if not competition.is_registration_open:
            raise ArkavAPIException(
                detail=K_COMPETITION_REGISTRATION_CLOSED_DETAIL,
                code=K_COMPETITION_REGISTRATION_CLOSED,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # A user can't register in a competition if he/she already participated in the same competition
        if TeamMember.objects.filter(team__competition=competition, user=user).exists():
            raise ArkavAPIException(
                detail=K_COMPETITION_ALREADY_REGISTERED_DETAIL,
                code=K_COMPETITION_ALREADY_REGISTERED,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Create a new team led by the current user
            new_team = Team.objects.create(
                competition=competition,
                name=team_name,
                institution=team_institution,
                team_leader=user,
            )

            # Add the current user as team member
            TeamMember.objects.create(
                team=new_team,
                user=user,
                invitation_full_name=user.full_name,
                invitation_email=user.email,
            )
        except ValueError as e:
            raise ArkavAPIException(
                detail=str(e),
                code='create_team_fail',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return new_team

    @transaction.atomic
    def migrate_teams(self, teams, events):
        members = TeamMember.objects.filter(team__in=teams).distinct()
        attendees = []
        for member in members:
            attendee, _ = CheckInAttendee.objects.get_or_create(
                email=member.email,
                name=member.full_name,
            )
            attendees.append(attendee)
        for event in events:
            CheckInAttendance.objects.bulk_create([CheckInAttendance(
                event=event,
                attendee=attendee,
            ) for attendee in attendees])


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
            subject='Pendaftaran Tim Arkavidia 7.0',
            body=mail_text_message,
            to=[team_member.invitation_email]
        )
        mail.attach_alternative(mail_html_message, 'text/html')
        mail.send()
        team_member.save()

    @transaction.atomic
    def create_team_member(self, team_member_data, team_id, user):
        full_name = team_member_data['full_name']
        email = team_member_data['email'].lower()

        team = get_object_or_404(
            Team.objects.all(),
            id=team_id,
            team_members__user=user,
        )

        # Check whether registration is open for this competition
        if not team.competition.is_registration_open:
            raise ArkavAPIException(
                detail=K_COMPETITION_REGISTRATION_CLOSED_DETAIL,
                code=K_COMPETITION_REGISTRATION_CLOSED,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Check whether team is still participating in the competition
        if not team.is_participating:
            raise ArkavAPIException(
                detail=K_TEAM_NOT_PARTICIPATING_DETAIL,
                code=K_TEAM_NOT_PARTICIPATING,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Check whether this team is full
        if team.team_members.count() >= team.competition.max_team_members:
            raise ArkavAPIException(
                detail=K_TEAM_FULL_DETAIL,
                code=K_TEAM_FULL,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            member_user = User.objects.get(email=email)
            if team.team_members.filter(user=member_user).exists():
                raise ArkavAPIException(
                    detail=K_TEAM_HAS_SELECTED_MEMBER_DETAIL,
                    code=K_TEAM_HAS_SELECTED_MEMBER,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if member_user.teams.filter(competition=team.competition).exists():
                raise ArkavAPIException(
                    detail=K_COMPETITION_ALREADY_REGISTERED_DETAIL,
                    code=K_COMPETITION_ALREADY_REGISTERED,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            # The user specified by the email is present, directly add to team
            new_team_member = TeamMember.objects.create(
                team=team,
                user=member_user,
                invitation_full_name=member_user.full_name,
                invitation_email=member_user.email,
            )
        except User.DoesNotExist:
            # The user specified by the email is not present, send invitation
            new_team_member = TeamMember.objects.create(
                team=team,
                invitation_full_name=full_name,
                invitation_email=email,
            )

        self.send_invitation_email(new_team_member)
        return new_team_member


class TaskResponseService:

    @transaction.atomic
    def submit_task_response(self, task_response_data, team_id, task_id, user):
        # Only team members can submit a response
        team = get_object_or_404(
            Team.objects.all(),
            id=team_id,
            team_members__user=user,
        )
        team_member = get_object_or_404(
            TeamMember.objects.all(),
            team_id=team_id,
            user=user,
        )

        if not team.is_participating:
            raise ArkavAPIException(
                detail=K_TEAM_NOT_PARTICIPATING_DETAIL,
                code=K_TEAM_NOT_PARTICIPATING,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # A team can only respond to tasks in the currently active stage
        task = get_object_or_404(
            Task.objects.all(),
            id=task_id,
            stage=team.active_stage,
        )

        response = task_response_data['response']

        # Create or update this TaskResponse, setting its status to awaiting_validation or completed
        # according to the whether this task requires validation,
        # and also updating its last_submitted_at.
        if task.requires_validation:
            task_response_status = AbstractTaskResponse.AWAITING_VALIDATION
        else:
            task_response_status = AbstractTaskResponse.COMPLETED

        new_task_response = None
        if task.is_user_task:
            task_team_member = task_response_data.get('team_member', team_member)
            new_task_response, created = UserTaskResponse.objects.update_or_create(
                task=task,
                team=team,
                team_member=task_team_member,
                defaults={
                    'response': response,
                    'status': task_response_status,
                    'last_submitted_at': timezone.now(),
                },
            )
        else:
            new_task_response, created = TaskResponse.objects.update_or_create(
                task=task,
                team=team,
                defaults={
                    'response': response,
                    'status': task_response_status,
                    'last_submitted_at': timezone.now(),
                },
            )

        return new_task_response

    @transaction.atomic
    def accept_task_response(self, task_response):
        task_response.reason = ''
        task_response.status = TaskResponse.COMPLETED
        task_response.save()

        users = []
        if task_response.task.is_user_task:
            if task_response.team_member.user is not None:
                users = [task_response.team_member.user]
        else:
            users = task_response.team.members.all()
        AnnouncementService().send_announcement(
            title="{} Task Completion".format(task_response.task),
            message="Submisi berkas Anda untuk {} sudah diverifikasi dan diterima".format(
                task_response.task),
            users=users,
        )

    @transaction.atomic
    def reject_task_response(self, task_response, reason):
        task_response.reason = reason
        task_response.status = TaskResponse.REJECTED
        task_response.save()

        users = []
        if task_response.task.is_user_task:
            if task_response.team_member.user is not None:
                users = [task_response.team_member.user]
        else:
            users = task_response.team.members.all()
        AnnouncementService().send_announcement(
            title="{} Task Rejection".format(task_response.task),
            message="Submisi berkas Anda untuk {} ditolak, lihat alasannya pada tab Competition!".format(
                task_response.task),
            users=users,
        )
