from django.db import models
from arkav.arkavauth.models import User
import uuid


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.content


class Session(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start = models.DateTimeField(auto_now_add=True, editable=False)
    end = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(to=User, related_name='submission', on_delete=models.CASCADE, unique=True)


class QuestionImage(models.Model):
    question = models.ForeignKey(to=Question, related_name='question_images', on_delete=models.CASCADE)
    url = models.CharField(max_length=255)


class Choice(models.Model):
    content = models.TextField()
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(to=Question, related_name='choices', on_delete=models.CASCADE)

    def __str__(self):
        return self.tag + " " + self.content


class ChoiceImage(models.Model):
    choice = models.ForeignKey(to=Choice, related_name='choice_images', on_delete=models.CASCADE)
    url = models.CharField(max_length=255)


class Answer(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    submission = models.ForeignKey(to=Submission, related_name='answer', on_delete=models.CASCADE)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)

    @property
    def tag(self):
        return self.choice.tag

    class Meta:
        unique_together = (('submission', 'question'))
