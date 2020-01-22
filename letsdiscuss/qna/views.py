from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import action

from .models import *
from .serializers import *
from letsdiscuss.users.models import User

class QuestionViewSet(viewsets.ViewSet):
    

    def list(self, request):
        queryset = Question.objects.all()
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)


    def retrieve(self, request, pk=None):
        try:
            original_question = Question.objects.get(id=pk)    
        except Question.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)
        read_serializer = QuestionSerializer(original_question)
        return Response(read_serializer.data)


    def create(self, request):
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