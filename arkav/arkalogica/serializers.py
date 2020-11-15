from rest_framework import serializers
from django.template import engines
from arkav.arkalogica.models import Session, Question, Answer
from arkav.arkalogica.models import Submission, Choice

django_engine = engines['django']


class ChoiceSerializer(serializers.ModelSerializer):
    choice_images = serializers.StringRelatedField(many=True)
    tag = serializers.SerializerMethodField()

    def get_tag(self, obj):
        return obj.tag()

    class Meta:
        model = Choice
        fields = ('tag', 'content', 'choice_images',)
        read_only_fields = ('content', 'choice_images',)


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    question_images = serializers.StringRelatedField(many=True)

    class Meta:
        model = Question
        fields = ('id', 'title', 'content', 'question_images', 'choices')
        read_only_fields = ('id', 'title', 'content', 'question_images', 'choices')


class SessionSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = ('id', 'title', 'description', 'start_time', 'end_time', 'question',)
        read_only_fields = ('id', 'title', 'description', 'start_time', 'end_time', 'question',)


class AnswerRespSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()

    def get_tag(self, obj):
        return obj.tag()

    class Meta:
        model = Answer
        fields = ('question', 'tag',)
        read_only_fields = ('question', 'tag',)


class AnswerReqSerializer(serializers.ModelSerializer):
    tag = serializers.CharField(min_length=1, max_length=1)

    class Meta:
        model = Answer
        fields = ('question', 'tag',)


class SubmissionSerializer(serializers.ModelSerializer):
    answer = AnswerRespSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = ('id', 'start', 'end', 'answer',)
        read_only_fields = ('id', 'start', 'end', 'answer',)
