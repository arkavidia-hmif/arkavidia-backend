from rest_framework import serializers
from django.template import engines
from arkav.arkalogica.models import Session, Question, Answer
from arkav.arkalogica.models import Submission, Choice

django_engine = engines['django']


class ChoiceSerializer(serializers.ModelSerializer):
    choice_images = serializers.StringRelatedField(many=True)

    class Meta:
        model = Choice
        fields = ('tag', 'content', 'choice_images',)
        read_only_fields = ('content', 'choice_images',)


class QuestionSerializer(serializers.ModelSerializer):
    question_images = serializers.StringRelatedField(many=True)
    choices = serializers.SerializerMethodField()

    def get_choices(self, obj):
        data = ChoiceSerializer(obj.choices.all(), many=True).data
        return data

    class Meta:
        model = Question
        fields = ('id', 'title', 'content', 'question_images', 'choices')
        read_only_fields = ('id', 'title', 'content', 'question_images', 'choices')


class SessionSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    def get_questions(self, obj):
        data = QuestionSerializer(Question.objects.all(), many=True).data
        return data

    class Meta:
        model = Session
        fields = ('id', 'title', 'description', 'start_time', 'end_time', 'questions',)
        read_only_fields = ('id', 'title', 'description', 'start_time', 'end_time', 'questions',)


class AnswerRespSerializer(serializers.ModelSerializer):
    tag = serializers.SerializerMethodField()

    def get_tag(self, obj):
        return obj.choice.tag

    class Meta:
        model = Answer
        fields = ('question', 'tag')
        read_only_fields = ('question', 'tag')


class AnswerReqSerializer(serializers.Serializer):
    tag = serializers.CharField(min_length=1, max_length=1)
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())

    class Meta:
        fields = ('question', 'tag',)


class SubmissionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    def get_answers(self, obj):
        data = AnswerRespSerializer(obj.answer.all(), many=True).data
        return data

    class Meta:
        model = Submission
        fields = ('id', 'start', 'end', 'answers',)
        read_only_fields = ('id', 'start', 'end', 'answers',)
