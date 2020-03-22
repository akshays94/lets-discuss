from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action

from letsdiscuss.qna.models import Question, QuestionStarred, QuestionVote, Answer
from letsdiscuss.users.models import User
from letsdiscuss.qna.reputation_engine import ReputationEngine
from letsdiscuss.qna.serializers1.questions import QuestionModelSerializer, CreateQuestionSerializer

from letsdiscuss.qna.mixins.read_write_serializer_mixin import ReadWriteSerializerMixin
from letsdiscuss.qna.serializers1.answers import AnswerModelSerializer, CreateAnswerSerializer


class QuestionViewSet(ReadWriteSerializerMixin, viewsets.ModelViewSet):

  queryset                = Question.objects.all().order_by('-created_on')
  read_serializer_class   = QuestionModelSerializer
  write_serializer_class  = CreateQuestionSerializer

  def destroy(self, request, pk=None):
    try:
      original_question = Question.objects.get(id=pk)    
    except Question.DoesNotExist:
      return Response(None, status=status.HTTP_404_NOT_FOUND)
    original_question.is_deleted = True
    original_question.deleted_by = request.user
    original_question.save()
    return Response()

  @action(methods=['post'], detail=True)
  def upvote(self, request, pk=None):
    voter = request.user
    try:
        original_question = Question.objects.get(id=pk)    
    except Question.DoesNotExist:
        return Response({'message': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

    try: 
      question_vote = QuestionVote.objects.get(created_by=voter, question_id=pk)
      
      if question_vote.is_upvote:
        return Response({'message': 'ALREADY UPVOTED'}, status=status.HTTP_409_CONFLICT)
      else:
        question_vote.is_upvote = True
        question_vote.modified_by = voter
        question_vote.save()
        
    except QuestionVote.DoesNotExist:
      question_vote = QuestionVote.objects.create(**{
          'question': original_question,
          'is_upvote': True,
          'created_by': voter,
          'modified_by': voter
      })

      ReputationEngine(
        instance=question_vote, 
        initiator=voter).create_score_question_upvote()

      return Response({'message': 'UPVOTED'})


  @action(methods=['post'], detail=True)
  def downvote(self, request, pk=None):
    voter = request.user
    try:
        original_question = Question.objects.get(id=pk)    
    except Question.DoesNotExist:
        return Response({'message': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

    try: 
      question_vote = QuestionVote.objects.get(created_by=voter, question_id=pk)
      
      if not question_vote.is_upvote:
          return Response({'message': 'ALREADY DOWNVOTED'}, status=status.HTTP_409_CONFLICT)
      else:
          question_vote.is_upvote = False
          question_vote.modified_by = voter
          question_vote.save()

    except QuestionVote.DoesNotExist:
      question_vote = QuestionVote.objects.create(**{
          'question': original_question,
          'is_upvote': False,
          'created_by': voter,
          'modified_by': voter
      })

    ReputationEngine(
      instance=question_vote, 
      initiator=voter).create_score_question_downvote()

    return Response({'message': 'DOWNVOTED'})

    
  @action(url_path="revoke-vote", methods=['post'], detail=True)
  def revoke_vote(self, request, pk=None):
    voter = request.user
    try:
        original_question = Question.objects.get(id=pk)    
    except Question.DoesNotExist:
        return Response({'message': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

    try: 
      question_vote = QuestionVote.objects.get(created_by=voter, question_id=pk)
      
      ReputationEngine(
        instance=question_vote, 
        initiator=voter).delete_score_revoke_vote()

      question_vote.delete()

      upvotes = QuestionVote.objects.filter(question=original_question, is_upvote=True).count()    
      downvotes = QuestionVote.objects.filter(question=original_question, is_upvote=False).count()    
      original_question.votes = upvotes - downvotes
      original_question.save()

        
      return Response({'message': 'VOTE REVOKED'})

    except QuestionVote.DoesNotExist:
      return Response({'message': 'NOT VOTED'})  


  @action(methods=['get', 'post'], detail=True)
  def answers(self, request, pk=None):
      
    if request.method == 'GET':
        
      queryset = Answer.objects.filter(question=pk).order_by('-is_correct', '-created_on')
      serializer = AnswerModelSerializer(
                      queryset, context={ 'request': request }, many=True)
      return Response(serializer.data)
    
    else:

      try:
          question = Question.objects.get(id=pk)
      except Question.DoesNotExist:
          return Response({'message': 'Question does not exist'}, status=status.HTTP_404_NOT_FOUND)

      data = request.data
      if type(data) != dict:
        data = request.data.dict()
      data.update({
          'question': question,
          'created_by': request.user,
          'modified_by': request.user
      })
      write_serializer = CreateAnswerSerializer(data=data, context={ 'request': request })
      write_serializer.is_valid(raise_exception=True)
      instance = write_serializer.create(data)
      return Response()


  @action(methods=['get'], detail=True)
  def votes(self, request, pk=None):
    try:
      original_question = Question.objects.get(id=pk)
      return Response({
        'votes': original_question.votes
      })   
    except Question.DoesNotExist:
      return Response({'message': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)


  @action(url_path="mark-star", methods=['post'], detail=True)
  def mark_star(self, request, pk=None):
    voter = request.user
    try:
        original_question = Question.objects.get(id=pk)    
    except Question.DoesNotExist:
        return Response({'message': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

    is_already_starred = QuestionStarred.objects.filter(question=original_question, created_by=voter).exists()

    if is_already_starred:
      return Response({'message': 'Already starred'}, status=status.HTTP_409_CONFLICT)

    QuestionStarred.objects.create(**{
      'question': original_question,
      'created_by': voter,
      'modified_by': voter
    })
    return Response({'message': 'STARRED'})


  @action(url_path="unmark-star", methods=['post'], detail=True)
  def unmark_star(self, request, pk=None):
    voter = request.user
    try:
        original_question = Question.objects.get(id=pk)    
    except Question.DoesNotExist:
        return Response({'message': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

    is_already_starred = QuestionStarred.objects.filter(question=original_question, created_by=voter)

    if is_already_starred.exists():
      is_already_starred.delete()
      return Response({'message': 'UNSTARRED'})
    
    return Response({'message': 'Already unstarred'}, status=status.HTTP_404_NOT_FOUND)   





