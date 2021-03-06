from arkav.arkavauth.constants import EDUCATION_LEVEL_CHOICES
from arkav.arkavauth.models import User
from arkav.uploader.models import UploadedFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import jsonfield
import uuid


@receiver(post_save, sender=User)
def handle_user_post_save(sender, instance, created, **kwargs):
    '''
    Connect newly registered user with any teams
    in which he/she has been registered as a member.
    '''
    if created:
        newly_registered_team_members = TeamMember.objects.filter(
            user__isnull=True,
            invitation_email=instance.email,
        )
        for team_member in newly_registered_team_members:
            team_member.user = instance
            team_member.invitation_full_name = instance.full_name
            team_member.save()


class Competition(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    education_level = models.CharField(max_length=30, null=True, default=None, choices=EDUCATION_LEVEL_CHOICES)
    max_team_members = models.IntegerField(default=1)
    min_team_members = models.IntegerField(default=1)
    is_registration_open = models.BooleanField(default=True)
    view_icon = models.URLField(default='')

    def __str__(self):
        return self.name


class Stage(models.Model):
    '''
    A competition contains one or more stages, e.g. registration, qualification and final stages.
    The ordering of stages is specified manually as an integer, with respect to competition.
    '''
    competition = models.ForeignKey(to=Competition, related_name='stages', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    def __str__(self):
        return '%s - %s' % (self.competition.name, self.name)

    class Meta:
        ordering = ['competition', 'order']


class TaskCategory(models.Model):
    '''
    The category label for this task, e.g. payment, proposal upload, etc.
    Used to help staff filter relevant tasks.
    '''
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'task categories'


class TaskWidget(models.Model):
    '''
    The type of widget (component) to be shown to the user for completing this task,
    e.g. text_input, file_upload.
    '''
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    '''
    A stage contains one or more tasks, e.g. payment, upload proposal, etc.
    '''
    stage = models.ForeignKey(to=Stage, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    category = models.ForeignKey(to=TaskCategory, related_name='tasks', on_delete=models.PROTECT)
    widget = models.ForeignKey(to=TaskWidget, related_name='tasks', on_delete=models.PROTECT)
    widget_parameters = jsonfield.JSONField(null=True)
    requires_validation = models.BooleanField(default=False)
    is_user_task = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.stage.competition.name, self.name)


class Team(models.Model):
    '''
    A competition can have participating teams.
    - A team can only see stages up to the active_stage;
      stages which comes after the active_stage are not visible.
    - A team can only respond to tasks in the currently active stage
      and only if is_participating is True; all other stages are locked.
    - active_stage defaults to the first stage in the team's competition;
      creation fails if the team's competition does not have a stage yet.
    '''
    competition = models.ForeignKey(to=Competition, related_name='teams', on_delete=models.PROTECT)
    name = models.CharField(max_length=50, unique=True)
    institution = models.CharField(max_length=100)
    members = models.ManyToManyField(to=User, related_name='teams', through='TeamMember')
    team_leader = models.ForeignKey(to=User, related_name='led_teams', on_delete=models.PROTECT)
    active_stage = models.ForeignKey(to=Stage, related_name='active_teams', on_delete=models.PROTECT)
    is_participating = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{:03d} - {}'.format(self.id, self.name)

    @property
    def has_completed_active_stage(self):
        '''
        Whether the team has already complete all the task in the active stage or not
        '''
        active_stage_task_count = self.active_stage.tasks.count()

        active_stage_completed_task_count = (
            self.task_responses.filter(task__stage=self.active_stage, status=TaskResponse.COMPLETED).count() +
            self.user_task_responses.filter(task__stage=self.active_stage, status=TaskResponse.COMPLETED)
                                    .count() // self.team_members.count()
        )
        return active_stage_task_count == active_stage_completed_task_count

    @property
    def visible_stages(self):
        '''
        A team can only see stages up to the active_stage;
        stages which comes after the active_stage should not be visible.
        '''
        return self.competition.stages.filter(order__lte=self.active_stage.order)

    def save(self, *args, **kwargs):
        # Use the first stage of the competition as the default for active_stage.
        # Will fail if no competition is set or the competition does not have a stage yet.
        if self.pk is None and not hasattr(self, 'active_stage'):
            try:
                competition_first_stage = self.competition.stages.first()
            except AttributeError as err:
                raise ValueError('Team must have a competition set.') from err
            if competition_first_stage is None:
                raise ValueError('Team must have a competition with at least 1 stage.')
            if Team.objects.filter(team_leader=self.team_leader).exclude(id=self.id).count() > 0:
                raise ValueError('User cannot lead more than 1 team.')
            self.active_stage = competition_first_stage

        super(Team, self).save(*args, **kwargs)

    class Meta:
        get_latest_by = 'created_at'


class TeamMember(models.Model):
    '''
    Many-to-many through/pivot table between Team and User.
    User can be None if not registered yet (still inviting).
    '''
    team = models.ForeignKey(to=Team, related_name='team_members', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, related_name='team_members', null=True, blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    # These fields are for storing invitations to the team, i.e. when user is null
    # When this TeamMember has user, use user.full_name and user.email
    invitation_full_name = models.CharField(max_length=75)
    invitation_email = models.EmailField()

    @property
    def has_account(self):
        return self.user is not None

    @property
    def full_name(self):
        if self.has_account:
            return self.user.full_name
        else:
            return self.invitation_full_name

    @property
    def email(self):
        if self.has_account:
            return self.user.email
        else:
            return self.invitation_email

    @property
    def is_team_leader(self):
        return self.email == self.team.team_leader.email

    def __str__(self):
        if self.has_account:
            return '%s - %s (%s)' % (self.team.name, self.user.full_name, self.user.email)
        else:
            return '%s - %s (%s)' % (self.team.name, self.invitation_full_name, self.invitation_email)

    class Meta:
        unique_together = (('team', 'user'),)  # Each team-user pair must be unique
        get_latest_by = 'created_at'


class AbstractTaskResponse(models.Model):
    '''
    A response to a task, e.g. proof of payment image, uploaded proposal.
    A TaskResponse will be created when a response is submitted for a task.
    Each team can only have at most 1 task response per task;
    resubmissions will update the existing TaskResponse and reset its state to awaiting_validation.
    If a task response is rejected, the reason should be detailed on reason.
    '''
    AWAITING_VALIDATION = 'awaiting_validation'
    COMPLETED = 'completed'
    REJECTED = 'rejected'
    STATUS_CHOICES = (
        (AWAITING_VALIDATION, 'Awaiting validation'),
        (COMPLETED, 'Completed'),
        (REJECTED, 'Rejected'),
    )

    task = models.ForeignKey(to=Task, related_name='task_responses', on_delete=models.PROTECT)
    team = models.ForeignKey(to=Team, related_name='task_responses', on_delete=models.CASCADE)
    response = models.TextField()
    reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    last_submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s - %s' % (self.task.name, self.team.name)

    @property
    def response_or_link(self):
        '''
        Return file link if response is valid uuid of an UploadedFile and is it a link
        '''
        try:
            uuid_response = uuid.UUID(self.response)
            response_file = UploadedFile.objects.filter(id=str(uuid_response)).first()
            if response_file is not None:
                return (response_file.file_link, True)
            return (self.response, False)
        except ValueError:
            return (self.response, False)

    def save(self, *args, **kwargs):
        # If this response's task's requires_validation is True,
        # use awaiting_validation as the default state, else use completed.
        if self.pk is None and (self.status is None or self.status == ''):
            if self.task.requires_validation:
                self.status = self.AWAITING_VALIDATION
            else:
                self.status = self.COMPLETED

        super().save(*args, **kwargs)

    class Meta:
        # Each team can only have at most 1 task response per task
        unique_together = (('task', 'team'),)
        get_latest_by = 'created_at'
        abstract = True


class TaskResponse(AbstractTaskResponse):

    class Meta:
        # Each team can only have at most 1 task response per task
        unique_together = (('task', 'team'),)
        get_latest_by = 'created_at'


class UserTaskResponse(AbstractTaskResponse):
    team_member = models.ForeignKey(to=TeamMember, related_name='user_task_responses',
                                    on_delete=models.CASCADE, null=True)
    task = models.ForeignKey(to=Task, related_name='user_task_responses', on_delete=models.PROTECT)
    team = models.ForeignKey(to=Team, related_name='user_task_responses', on_delete=models.CASCADE)

    class Meta:
        # Each user in team can only have at most 1 task response per task
        unique_together = (('task', 'team', 'team_member'),)
        get_latest_by = 'created_at'
