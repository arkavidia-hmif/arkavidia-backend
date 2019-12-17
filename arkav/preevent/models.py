from arkav.arkavauth.models import User
from arkav.uploader.models import UploadedFile
from django.db import models
from django.utils import timezone
import jsonfield
import uuid


class Preevent(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    subtitle = models.CharField(max_length=100, blank=True)
    is_registration_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Stage(models.Model):
    '''
    A preevent contains one or more stages, e.g. registration, qualification and final stages.
    The ordering of stages is specified manually as an integer, with respect to preevent.
    '''
    preevent = models.ForeignKey(to=Preevent, related_name='stages', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    def __str__(self):
        return '%s - %s' % (self.preevent.name, self.name)

    class Meta:
        ordering = ['preevent', 'order']


class TaskCategory(models.Model):
    '''
    The category label for this task, e.g. payment, resume upload, etc.
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
    A stage contains one or more tasks, e.g. payment, upload resume, etc.
    '''
    stage = models.ForeignKey(to=Stage, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    category = models.ForeignKey(to=TaskCategory, related_name='tasks', on_delete=models.PROTECT)
    widget = models.ForeignKey(to=TaskWidget, related_name='tasks', on_delete=models.PROTECT)
    widget_parameters = jsonfield.JSONField(null=True)
    requires_validation = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.stage.preevent.name, self.name)


class Registrant(models.Model):
    '''
    A preevent can have participating registrants.
    - A registrant can only see stages up to the active_stage;
      stages which comes after the active_stage are not visible.
    - A registrant can only respond to tasks in the currently active stage
      and only if is_participating is True; all other stages are locked.
    - active_stage defaults to the first stage in the registrant's preevent;
      creation fails if the registrant's preevent does not have a stage yet.
    '''
    preevent = models.ForeignKey(to=Preevent, related_name='registrants', on_delete=models.PROTECT)
    user = models.ForeignKey(to=User, related_name='preevent_registrants', on_delete=models.PROTECT)
    active_stage = models.ForeignKey(to=Stage, related_name='active_registrants', on_delete=models.PROTECT)
    is_participating = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{:03d} - {}'.format(self.id, self.user)

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def current_education(self):
        return self.user.current_education

    @property
    def institution(self):
        return self.user.institution

    @property
    def phone_number(self):
        return self.user.phone_number

    @property
    def address(self):
        return self.user.address

    @property
    def birth_date(self):
        return self.user.birth_date

    @property
    def has_completed_active_stage(self):
        active_stage_task_count = self.active_stage.tasks.count()
        active_stage_completed_task_count = self.task_responses.filter(
            task__stage=self.active_stage, status=TaskResponse.COMPLETED).count()
        return active_stage_task_count == active_stage_completed_task_count

    @property
    def visible_stages(self):
        '''
        A registrant can only see stages up to the active_stage;
        stages which comes after the active_stage should not be visible.
        '''
        return self.preevent.stages.filter(order__lte=self.active_stage.order)

    def save(self, *args, **kwargs):
        # Use the first stage of the preevent as the default for active_stage.
        # Will fail if no preevent is set or the preevent does not have a stage yet.
        if self.pk is None and not hasattr(self, 'active_stage'):
            try:
                preevent_first_stage = self.preevent.stages.first()
            except AttributeError as err:
                raise ValueError('Registrant must have a pre event set.') from err
            if preevent_first_stage is None:
                raise ValueError('Registrant must have a pre event with at least 1 stage.')
            self.active_stage = preevent_first_stage

        super(Registrant, self).save(*args, **kwargs)

    class Meta:
        get_latest_by = 'created_at'


class TaskResponse(models.Model):
    '''
    A response to a task, e.g. proof of payment image, uploaded proposal.
    A TaskResponse will be created when a response is submitted for a task.
    Each registrant can only have at most 1 task response per task;
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
    registrant = models.ForeignKey(to=Registrant, related_name='task_responses', on_delete=models.CASCADE)
    response = models.TextField()
    reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    last_submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return '%s - %s' % (self.task.name, self.registrant.user)

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
        # Each registrant can only have at most 1 task response per task
        unique_together = (('task', 'registrant'),)
        get_latest_by = 'created_at'
