from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import action

from letsdiscuss.qna.models import *
from letsdiscuss.qna.serializers import *
from letsdiscuss.users.models import User
from letsdiscuss.qna.reputation_engine import ReputationEngine

class AnswerViewSet(viewsets.ViewSet):
    
    def update(self, request, pk=None):
        data = request.data.dict()
        data.update({
            'created_by': request.user.id
        })
        write_serializer = CreateAnswerSerializer(data=data)
        write_serializer.is_valid(raise_exception=True)

        original_answer = Answer.objects.get(id=pk)
        instance = write_serializer.update(original_answer, data)
        
        read_serializer = AnswerSerializer(instance)
        return Response(read_serializer.data)


    def destroy(self, request, pk=None):
        try:
            original_answer = Answer.objects.get(id=pk)    
        except Answer.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND) 
        read_serializer = AnswerSerializer(original_answer)

        original_answer.is_deleted = True
        original_answer.deleted_by = request.user
        original_answer.save()

        return Response(read_serializer.data)

    
    @action(methods=['post'], detail=True)
    def upvote(self, request, pk=None):
        voter = request.user
        try:
            original_answer = Answer.objects.get(id=pk)    
        except Answer.DoesNotExist:
            return Response({'message': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)

        try: 
            answer_vote = AnswerVote.objects.get(created_by=voter, answer_id=pk)
            
            if answer_vote.is_upvote:
                return Response({'message': 'ALREADY UPVOTED'}, status=status.HTTP_409_CONFLICT)
            else:
                answer_vote.is_upvote = True
                answer_vote.modified_by = voter
                answer_vote.save()

        except AnswerVote.DoesNotExist:
            answer_vote = AnswerVote.objects.create(**{
                'answer': original_answer,
                'is_upvote': True,
                'created_by': voter,
                'modified_by': voter
            })
        
        ReputationEngine(
          instance=answer_vote, 
          initiator=voter).create_score_answer_upvote()

        return Response({'message': 'UPVOTED'})


    @action(methods=['post'], detail=True)
    def downvote(self, request, pk=None):
        voter = request.user
        try:
            original_answer = Answer.objects.get(id=pk)    
        except Answer.DoesNotExist:
            return Response({'message': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)

        try: 
            answer_vote = AnswerVote.objects.get(created_by=voter, answer_id=pk)
            
            if not answer_vote.is_upvote:
                return Response({'message': 'ALREADY DOWNVOTED'}, status=status.HTTP_409_CONFLICT)
            else:
                answer_vote.is_upvote = False
                answer_vote.modified_by = voter
                answer_vote.save()

        except AnswerVote.DoesNotExist:
            answer_vote = AnswerVote.objects.create(**{
                'answer': original_answer,
                'is_upvote': False,
                'created_by': voter,
                'modified_by': voter
            })

        return Response({'message': 'DOWNVOTED'})


    @action(url_path='mark-as-correct', methods=['post'], detail=True)
    def mark_as_correct(self, request, pk=None):
        voter = request.user
        try:
            original_answer = Answer.objects.get(id=pk)    
        except Answer.DoesNotExist:
            return Response({'message': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)

        is_other_answer_already_marked = Answer.objects.filter(question=original_answer.question, is_correct=True).exists()

        if is_other_answer_already_marked:
          return Response({'message': 'Some answer of this question is already marked as correct'}, status=status.HTTP_409_CONFLICT)
        else:
          original_answer.is_correct = True
          original_answer.modified_by = voter
          original_answer.save()
          return Response({'message': 'MARKED CORRECT'})


    @action(url_path="revoke-vote", methods=['post'], detail=True)
    def revoke_vote(self, request, pk=None):
        voter = request.user
        try:
            original_answer = Answer.objects.get(id=pk)    
        except Answer.DoesNotExist:
            return Response({'message': 'Answer not found'}, status=status.HTTP_404_NOT_FOUND)

        try: 
            answer_vote = AnswerVote.objects.get(created_by=voter, answer_id=pk)
            
            answer_vote.delete()

            upvotes = AnswerVote.objects.filter(answer=original_answer, is_upvote=True).count()    
            downvotes = AnswerVote.objects.filter(answer=original_answer, is_upvote=False).count()    
            original_answer.votes = upvotes - downvotes
            original_answer.save()

            ReputationEngine(
              instance=answer_vote, 
              initiator=voter).delete_score_answer_revoke_vote()

            return Response({'message': 'VOTE REVOKED'}) 

        except AnswerVote.DoesNotExist:
          return Response({'message': 'NOT VOTED'})        

