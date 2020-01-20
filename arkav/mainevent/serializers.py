from rest_framework import serializers
from arkav.arkavauth.serializers import UserSerializer
from arkav.mainevent.models import Mainevent
from arkav.mainevent.models import Stage
from arkav.mainevent.models import Task
from arkav.mainevent.models import Registrant
from arkav.mainevent.models import TaskResponse
from django.template import engines

django_engine = engines['django']


class MaineventSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Mainevent
        fields = ('id', 'name', 'slug', 'category', 'is_registration_open',
                  'short_desc', 'begin_time', 'end_time', 'order')
        read_only_fields = ('id', 'name', 'slug', 'category', 'is_registration_open',
                            'short_desc', 'begin_time', 'end_time', 'order')


class MaineventDetailsSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Mainevent
        fields = ('id', 'name', 'slug', 'category', 'is_registration_open',
                  'short_desc', 'long_desc', 'begin_time', 'end_time', 'order')
        read_only_fields = ('id', 'name', 'slug', 'category', 'is_registration_open',
                            'short_desc', 'long_desc', 'begin_time', 'end_time', 'order')


class TaskSerializer(serializers.ModelSerializer):
    widget = serializers.SlugRelatedField(slug_field='name', read_only=True)
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'name', 'category', 'widget', 'widget_parameters')
        read_only_fields = ('id', 'name', 'category', 'widget', 'widget_parameters')
        ref_name = 'MaineventTaskSerializer'


class StageSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Stage
        fields = ('id', 'name', 'order', 'tasks')
        read_only_fields = ('id', 'name', 'order', 'tasks')
        ref_name = 'MaineventStageSerializer'


class TaskResponseSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(source='task', read_only=True)

    class Meta:
        model = TaskResponse
        fields = ('task_id', 'response', 'status', 'reason', 'last_submitted_at')
        read_only_fields = ('task_id', 'status', 'reason', 'last_submitted_at')
        ref_name = 'MaineventTaskResponseSerializer'


class RegistrantSerializer(serializers.ModelSerializer):
    mainevent = MaineventSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Registrant
        fields = ('id', 'mainevent', 'user', 'is_participating')
        read_only_fields = ('id', 'mainevent', 'user', 'is_participating')
        ref_name = 'MaineventRegistrantSerializer'


class RegistrantDetailsSerializer(serializers.ModelSerializer):
    mainevent = MaineventSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    active_stage_id = serializers.PrimaryKeyRelatedField(source='active_stage', read_only=True)
    stages = StageSerializer(source='visible_stages', many=True, read_only=True)
    task_responses = TaskResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Registrant
        fields = (
            'id', 'mainevent', 'user', 'is_participating',
            'active_stage_id', 'stages', 'task_responses', 'created_at'
        )
        read_only_fields = (
            'id', 'mainevent', 'user',
            'active_stage_id', 'stages', 'task_responses', 'created_at',
        )
        ref_name = 'MaineventRegistrantDetailsSerializer'

    def to_representation(self, instance):
        '''
        Render task widget parameter as template
        '''
        registrant_data = super().to_representation(instance)
        for stage in registrant_data['stages']:
            for task in stage['tasks']:
                if 'description' in task['widget_parameters']:
                    template_string = django_engine.from_string(task['widget_parameters']['description'])
                    task['widget_parameters']['description'] = template_string.render(context={
                        'registrant': instance,
                        'registrant_number': '{:03d}'.format(instance.id)
                    })
        return registrant_data


class RegisterRegistrantRequestSerializer(serializers.Serializer):
    mainevent_id = serializers.PrimaryKeyRelatedField(queryset=Mainevent.objects.all())

    class Meta:
        ref_name = 'MaineventRegisterRegistrantRequestSerializer'
