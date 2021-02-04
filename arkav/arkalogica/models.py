from django.db import models
from django.utils import timezone
from arkav.arkavauth.models import User
import uuid


class Session(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    session = models.ForeignKey(to=Session, related_name='questions', on_delete=models.CASCADE)

    def __str__(self):
        return self.title + ": " + self.content


class Submission(models.Model):
    start = models.DateTimeField(auto_now_add=True, editable=False)
    end = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(to=User, related_name='submission', on_delete=models.CASCADE, unique=True)
    session = models.ForeignKey(to=Session, related_name='submission', on_delete=models.CASCADE, default=2)

    def __str__(self):
        return self.user.full_name + "'s Submission"


class QuestionImage(models.Model):
    question = models.ForeignKey(to=Question, related_name='question_images', on_delete=models.CASCADE)
    url = models.URLField()

    def __str__(self):
        return '%s' % self.url


class Choice(models.Model):
    tag = models.CharField(max_length=1)
    content = models.TextField()
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(to=Question, related_name='choices', on_delete=models.CASCADE)

    def __str__(self):
        return self.question.title + ": " + self.tag + ". " + self.content


class ChoiceImage(models.Model):
    choice = models.ForeignKey(to=Choice, related_name='choice_images', on_delete=models.CASCADE)
    url = models.URLField()

    def __str__(self):
        return '%s' % self.url


class Answer(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    submission = models.ForeignKey(to=Submission, related_name='answer', on_delete=models.CASCADE)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)

    @property
    def tag(self):
        return self.choice.tag

    class Meta:
        unique_together = (('submission', 'question'))
