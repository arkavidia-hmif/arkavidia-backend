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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)
    questions = models.ManyToManyField(to=Question, related_name='session')

    @property
    def question_count(self):
        return Session.objects.filter(question__id=self.id).count()


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start = models.DateTimeField(auto_now_add=True, editable=False)
    end = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(to=User, related_name='submission', on_delete=models.CASCADE)
    session = models.ForeignKey(to=Session, related_name='submission', on_delete=models.CASCADE)

    def answer_count(self):
        return Answer.objects.filter(answer__id=self.id).count()

    class Meta:
        unique_together = (('user', 'session'))


class QuestionImage(models.Model):
    question = models.ForeignKey(to=Question, related_name='question_image', on_delete=models.CASCADE)
    url = models.CharField(max_length=255)


class Choice(models.Model):
    tag = models.CharField(max_length=1)
    content = models.TextField()
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(to=Question, related_name='choice', on_delete=models.CASCADE)

    def __str__(self):
        return self.tag + " " + self.content


class ChoiceImage(models.Model):
    choice = models.ForeignKey(to=Choice, related_name='choice_image', on_delete=models.CASCADE)
    url = models.CharField(max_length=255)


class Answer(models.Model):
    tag = models.CharField(max_length=1)
    submission = models.ForeignKey(to=Submission, related_name='answer', on_delete=models.CASCADE)
    question = models.ForeignKey(to=Question, on_delete=models.CASCADE)

    @property
    def is_correct(self):
        choices = Choice.objects.filter(question=self.question).all()
        for choice in choices:
            if (choice.tag == self.tag) and (choice.is_correct):
                return True
        return False

    def __str__(self):
        return self.tag

    class Meta:
        unique_together = (('submission', 'question'))
