from rest_framework import serializers
from arkav.arkavauth.models import User
from arkav.arkavauth.serializers import UserSerializer
from arkav.preevent.models import Preevent
from arkav.preevent.models import Stage
from arkav.preevent.models import Task
from arkav.preevent.models import Registrant
from arkav.preevent.models import TaskResponse
from django.template import engines

django_engine = engines['django']


class PreeventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Preevent
        fields = ('id', 'name', 'slug', 'is_registration_open')
        read_only_fields = ('id', 'name', 'slug', 'is_registration_open')


class TaskSerializer(serializers.ModelSerializer):
    widget = serializers.CharField(source='widget.name')
    category = serializers.CharField(source='category.name')

    class Meta:
        model = Task
        fields = ('id', 'name', 'category', 'widget', 'widget_parameters')
        read_only_fields = ('id', 'name', 'category', 'widget', 'widget_parameters')
        ref_name = 'PreeventTaskSerializer'


class StageSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Stage
        fields = ('id', 'name', 'order', 'tasks')
        read_only_fields = ('id', 'name', 'order', 'tasks')
        ref_name = 'PreeventStageSerializer'


class TaskResponseSerializer(serializers.ModelSerializer):
    task_id = serializers.PrimaryKeyRelatedField(source='task', read_only=True)
    registrant_id = serializers.PrimaryKeyRelatedField(source='registrant',
                                                       queryset=Registrant.objects.all(), required=False)

    class Meta:
        model = TaskResponse
        fields = ('task_id', 'response', 'status', 'reason', 'last_submitted_at', 'registrant_id')
        read_only_fields = ('task_id', 'status', 'reason', 'last_submitted_at', 'registrant_id')
        ref_name = 'PreeventTaskResponseSerializer'


class RegistrantSerializer(serializers.ModelSerializer):
    preevent = PreeventSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Registrant
        fields = ('id', 'preevent', 'user',
                  'is_participating', 'category')
        read_only_fields = ('id', 'preevent', 'user',
                            'is_participating', 'category')


class RegistrantDetailsSerializer(serializers.ModelSerializer):
    preevent = PreeventSerializer(read_only=True)
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    user = UserSerializer(read_only=True)
    active_stage_id = serializers.PrimaryKeyRelatedField(source='active_stage', read_only=True)
    stages = StageSerializer(source='visible_stages', many=True, read_only=True)
    task_responses = TaskResponseSerializer(many=True, read_only=True)

    class Meta:
        model = Registrant
        fields = (
            'id', 'preevent', 'category', 'user',
            'is_participating', 'active_stage_id', 'stages',
            'task_responses', 'created_at'
        )
        read_only_fields = (
            'id', 'preevent', 'category', 'is_participating', 'user',
            'active_stage_id', 'stages', 'task_responses', 'created_at'
        )

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
                        'registrant_number': '{:03d}'.format(instance.id + 100)
                    })
        return registrant_data


class RegisterRegistrantRequestSerializer(serializers.Serializer):
    preevent_id = serializers.PrimaryKeyRelatedField(queryset=Preevent.objects.all())
