from rest_framework import serializers
from django.template import engines
from arkav.arkalogica.models import Session, Question, Answer

django_engine = engines['django']


class SessionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = ('id', 'title', 'description', 'start_time', 'end_time')
        read_only_fields = ('id', 'title', 'description', 'start_time', 'end_time')

class QuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ('id', 'title', 'content')
        read_only_fields = ('id', 'title', 'content')