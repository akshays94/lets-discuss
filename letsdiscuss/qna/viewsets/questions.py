from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import action

from letsdiscuss.qna.models import *
from letsdiscuss.qna.serializers import *
from letsdiscuss.users.models import User

class QuestionViewSet(viewsets.ViewSet):
    

    def list(self, request):
        queryset = Question.objects.all().order_by('-created_on')
        for question in queryset:
          the_question_vote = question.questionvote_set.filter(created_by=request.user.id)
          if the_question_vote.exists():
            the_question_vote = the_question_vote.first()
            question.is_voted = True
            question.is_upvoted = the_question_vote.is_upvote
            question.is_downvoted = the_question_vote.is_upvote == False
          else:
            question.is_voted = False
            question.is_upvoted = False
            question.is_downvoted = False    

        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        try:
            original_question = Question.objects.get(id=pk)
            the_question_vote = original_question.questionvote_set.filter(created_by=request.user.id)
            if the_question_vote.exists():
              the_question_vote = the_question_vote.first()
              original_question.is_voted = True
              original_question.is_upvoted = the_question_vote.is_upvote
              original_question.is_downvoted = the_question_vote.is_upvote == False
            else:
              original_question.is_voted = False
              original_question.is_upvoted = False
              original_question.is_downvoted = False   
        except Question.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        original_question.is_created_by_me = \
          original_question.created_by_id == request.user.id

        original_question.answer_marked_correct = original_question.answer_set.filter(is_correct=True).exists()      
        
        read_serializer = QuestionSerializer(original_question)
        return Response(read_serializer.data)


    def create(self, request):
        data = request.data
        if type(data) != dict:
          data = request.data.dict()
        data.update({
            'created_by': request.user.id
        })
        write_serializer = CreateQuestionSerializer(data=data)
        write_serializer.is_valid(raise_exception=True)
        instance = write_serializer.create(data)
        read_serializer = QuestionSerializer(instance)
        return Response(read_serializer.data)


    def update(self, request, pk=None):
        data = request.data.dict()
        data.update({
            'created_by': request.user.id
        })
        write_serializer = CreateQuestionSerializer(data=data)
        write_serializer.is_valid(raise_exception=True)

        original_question = Question.objects.get(id=pk)
        instance = write_serializer.update(original_question, data)
        
        read_serializer = QuestionSerializer(instance)
        return Response(read_serializer.data)


    def destroy(self, request, pk=None):
        try:
            original_question = Question.objects.get(id=pk)    
        except Question.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND) 
        read_serializer = QuestionSerializer(original_question)

        original_question.is_deleted = True
        original_question.deleted_by = request.user
        original_question.save()

        return Response(read_serializer.data)

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
            for answer in queryset:
              the_answer_vote = answer.answervote_set.filter(created_by=request.user.id)
              if the_answer_vote.exists():
                the_answer_vote = the_answer_vote.first()
                answer.is_voted = True
                answer.is_upvoted = the_answer_vote.is_upvote
                answer.is_downvoted = the_answer_vote.is_upvote == False
              else:
                answer.is_voted = False
                answer.is_upvoted = False
                answer.is_downvoted = False
            serializer = AnswerSerializer(queryset, many=True)
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
                'created_by': request.user.id
            })
            write_serializer = CreateAnswerSerializer(data=data)
            write_serializer.is_valid(raise_exception=True)
            instance = write_serializer.create(data)
            read_serializer = AnswerSerializer(instance)
            return Response(read_serializer.data)


    @action(methods=['get'], detail=True)
    def votes(self, request, pk=None):
        try:
            original_question = Question.objects.get(id=pk)
            return Response({
              'votes': original_question.votes
            })   
        except Question.DoesNotExist:
            return Response({'message': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)





