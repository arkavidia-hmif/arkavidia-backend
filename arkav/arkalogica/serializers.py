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
    tag = serializers.SerializerMethodField()

    def get_tag(self, obj):
        return obj.tag()

    class Meta:
        model = Choice
        fields = ('tag', 'content', 'images',)
        read_only_fields = ('content', 'images',)


class QuestionImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuestionImage
        fields = ('url',)
        read_only_fields = ('url',)


class QuestionSerializer(serializers.ModelSerializer):
    images = QuestionImageSerializer(source='question_image', many=True, read_only=True)
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'title', 'content', 'images', 'choices')
        read_only_fields = ('id', 'title', 'content', 'images', 'choices')


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
