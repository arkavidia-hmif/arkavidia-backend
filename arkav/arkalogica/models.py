from django.db import models
from arkav.arkavauth.models import User
import uuid

class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(null=True)
    user = models.ForeignKey(to=User, related_name='submission')
    session = models.ForeignKey(to=Session, related_name='submission')

    class Meta:
        unique_together = (('user', 'session'))

class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True, default='')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now_add=True)

    @property
    def question_count(self):
        return Session.objects.filter(questions__id=self.id).count()

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sessions = models.ManyToManyField(to=Session, related_name='question', null=True, delete=models.SET_NULL)
    content = models.TextField()

class QuestionImage(models.Model):
    question = models.ForeignKey(to=Question, related_name='question_image')
    url = models.CharField()

class Choice(models.Model):
    tag = models.CharField(max_length=1)
    content = models.TextField()
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(to=Question, related_name='choice')

class ChoiceImage(models.Model):
    choice = models.ForeignKey(to=Choice, related_name='choice_image')
    url = models.CharField()

class Answer(models.Model):
    tag = models.CharField(max_length=1)
    submission = models.ManyToMany(to=Submission, related_name='answers')
    question = models.ForeignKey(Question)
    class Meta:
        unique_together = (('submission', 'question'))