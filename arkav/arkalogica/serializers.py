from rest_framework import serializers
from django.template import engines
from arkav.arkalogica.models import Session, Question, Answer
from arkav.arkalogica.models import Submission, Choice, ChoiceImage, QuestionImage

django_engine = engines['django']


class ChoiceImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChoiceImage
        fields = ('url',)
        read_only_fields = ('url',)


class ChoiceSerializer(serializers.ModelSerializer):
    images = ChoiceImageSerializer(source='choice_image', many=True, read_only=True)

    class Meta:
        model = Choice
        fields = ('tag', 'content', 'question', 'images',)
        read_only_fields = ('content', 'images',)


class QuestionImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionImage
        fields = ('url',)
        read_only_fields = ('url',)


class QuestionSerializer(serializers.ModelSerializer):
    images = QuestionImageSerializer(source='question_image', many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'title', 'content', 'images',)
        read_only_fields = ('id', 'title', 'content', 'images',)


class SessionListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = ('id', 'title', 'description', 'start_time', 'end_time',)
        read_only_fields = ('id', 'title', 'description', 'start_time', 'end_time',)


class SessionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = ('id', 'title', 'description', 'start_time', 'end_time', 'question',)
        read_only_fields = ('id', 'title', 'description', 'start_time', 'end_time',)


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('question', 'tag',)


class SubmissionRespSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = ('id', 'start', 'end', 'session', 'answer')
        read_only_fields = ('id', 'start', 'end', 'session', 'answer')


class SubmissionReqSerializer(serializers.ModelSerializer):
    answer = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'start', 'end', 'session', 'answer',)
        read_only_fields = ('id', 'start', 'end',)
