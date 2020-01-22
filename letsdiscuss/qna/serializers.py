from rest_framework import serializers
from .models import *

from letsdiscuss.users.serializers import UserSerializer
from letsdiscuss.users.models import *

class QuestionSerializer(serializers.ModelSerializer):
    
    created_by = UserSerializer()

    class Meta:
        model = Question
        fields = [
            'id', 'title', 'content', 'votes', 'created_by', 'created_on'
        ] 


class CreateQuestionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Question
        fields = [
            'id', 'title', 'content', 'votes', 'created_by', 'created_on'
        ]

    def create(self, validated_data):

        created_by_id = validated_data.pop('created_by')
        created_by = User.objects.get(id=created_by_id)
        validated_data.update({
            'created_by': created_by,
            'modified_by': created_by
        })

        question = Question.objects.create(**validated_data)
        return question


    def update(self, instance, validated_data):

        created_by_id = validated_data.pop('created_by')
        created_by = User.objects.get(id=created_by_id)
        validated_data.update({
            'created_by': created_by,
            'modified_by': created_by
        })

        instance.title = validated_data.get('title')
        instance.content = validated_data.get('content')
        instance.modified_by = validated_data.get('modified_by')
        instance.save()

        return instance

