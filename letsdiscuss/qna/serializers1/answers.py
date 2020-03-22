from django.utils.timesince import timesince
from rest_framework.fields import CurrentUserDefault

from rest_framework import serializers
from letsdiscuss.qna.models import Answer
from letsdiscuss.users.serializers import UserSerializer


class AnswerModelSerializer(serializers.ModelSerializer):

  created_by = UserSerializer()
  is_upvoted = serializers.SerializerMethodField()
  is_downvoted = serializers.SerializerMethodField()
  created_on_humanized = serializers.SerializerMethodField()

  def get_is_upvoted(self, answer):
    user = self.context['request'].user
    return answer.answervote_set.filter(created_by=user, is_upvote=True).exists()

  def get_is_downvoted(self, answer):
    user = self.context['request'].user
    return answer.answervote_set.filter(created_by=user, is_upvote=False).exists()

  def get_created_on_humanized(self, answer):
    return timesince(answer.created_on)

  class Meta:
    model = Answer
    fields = [
      'id',
      'content',
      'votes',
      'created_by',
      'created_on',
      'is_correct',
      'is_upvoted',
      'is_downvoted',
      'created_on_humanized',
      'created_on'
    ]


class CreateAnswerSerializer(serializers.ModelSerializer):

  created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
  modified_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
  
  def create(self, validated_data):
    return Answer.objects.create(**validated_data)

  def update(self, answer, validated_data):
    answer.content = validated_data.get('content', answer.content)
    answer.save()
    return answer

  class Meta:
    model = Answer
    fields = [
      'id',
      'content',
      'votes',
      'created_by',
      'modified_by'
    ]  