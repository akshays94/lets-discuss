from django.utils.timesince import timesince
from rest_framework.fields import CurrentUserDefault

from rest_framework import serializers
from letsdiscuss.qna.models import Question
from letsdiscuss.users.serializers import UserSerializer


class QuestionModelSerializer(serializers.ModelSerializer):

  created_by                = UserSerializer()
  is_upvoted                = serializers.SerializerMethodField()
  is_downvoted              = serializers.SerializerMethodField()
  is_created_by_me          = serializers.SerializerMethodField()
  is_starred                = serializers.SerializerMethodField()
  created_on_humanized      = serializers.SerializerMethodField()
  answers_count             = serializers.SerializerMethodField()
  is_marked_correct_answer  = serializers.SerializerMethodField()


  def get_is_upvoted(self, question):
    user = self.context['request'].user
    return question.questionvote_set.filter(created_by=user, is_upvote=True).exists()


  def get_is_downvoted(self, question):
    user = self.context['request'].user
    return question.questionvote_set.filter(created_by=user, is_upvote=False).exists()


  def get_is_created_by_me(self, question):
    return question.created_by == self.context['request'].user   


  def get_is_starred(self, question):
    user = self.context['request'].user
    return question.questionstarred_set.filter(created_by=user).exists()


  def get_created_on_humanized(self, question):
    return timesince(question.created_on)


  def get_answers_count(self, question):
    return question.answer_set.count()


  def get_is_marked_correct_answer(self, question):
    return question.answer_set.filter(is_correct=True).exists()


  class Meta:    
    model = Question
    fields = [
      'id',
      'title',
      'content',
      'votes',
      'created_by',
      'is_upvoted',
      'is_downvoted',
      'is_created_by_me',
      'is_starred',
      'created_on_humanized',
      'created_on',
      'answers_count',
      'is_marked_correct_answer'
    ]



class CreateQuestionSerializer(serializers.ModelSerializer):
  
  created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
  modified_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
  
  def create(self, validated_data):
    return Question.objects.create(**validated_data)

  def update(self, question, validated_data):
    question.title = validated_data.get('title', question.title)
    question.content = validated_data.get('content', question.content)
    question.save()
    return question

  class Meta:
    model = Question
    fields = [
      'id',
      'title',
      'content',
      'votes',
      'created_by',
      'modified_by'
    ]


