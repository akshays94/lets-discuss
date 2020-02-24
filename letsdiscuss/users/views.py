from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from .models import User, UserReputation, UserMeta
from .permissions import IsUserOrReadOnly
from .serializers import CreateUserSerializer, UserSerializer, UserReputationSerializer, UserMetaSerializer

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response



class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    Updates and retrieves user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsUserOrReadOnly,)


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    Creates user accounts
    """
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)


class CustomAuthToken(ObtainAuthToken):

  def post(self, request, *args, **kwargs):
    serializer = self.serializer_class(data=request.data,
                                        context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    token, created = Token.objects.get_or_create(user=user)
    return Response({
        'auth_token': token.key,
        'id': user.pk,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    })

class UserLeaderboardViewSet(viewsets.ModelViewSet):
    """
    Get leaderboard
    """
    queryset = UserMeta.objects.exclude(score=0).order_by('-score')[:10]
    serializer_class = UserMetaSerializer


class UserReputationViewSet(viewsets.ViewSet):
  
  def retrieve(self, request, pk=None):
    try:
      user = User.objects.get(id=pk)
    except User.DoesNotExist as e:
      return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    reputations = \
        UserReputation.objects.filter(user=user).order_by('-created_on')
    
    for reputation in reputations:
      if reputation.category in ['ASAC1']:
        answer = reputation.answerer_reputation.all().first()
        reputation.instance = {
          'question_id': answer.question.id,
          'question_title': answer.question.title,
          'answer_content': answer.content
        }

      elif reputation.category in ['ASAC2']:
        answer = reputation.acceptor_reputation.all().first()
        reputation.instance = {
          'question_id': answer.question.id,
          'question_title': answer.question.title,
          'answer_content': answer.content
        }

      elif reputation.category in ['QUSUP', 'QUSDN']:
        question_vote = reputation.questionvote_set.all().first()
        reputation.instance = {
          'question_id': question_vote.question.id,
          'question_title': question_vote.question.title
        }

      elif reputation.category in ['ANSUP', 'ASDN1']:
        answer_vote = reputation.vote_reputation.all().first()
        reputation.instance = {
          'question_id': answer_vote.answer.question.id,
          'question_title': answer_vote.answer.question.title,
          'answer_content': answer_vote.answer.content
        }

      elif reputation.category in ['ASDN2']:
        answer_vote = reputation.downvote_reputation.all().first()
        reputation.instance = {
          'question_id': answer_vote.answer.question.id,
          'question_title': answer_vote.answer.question.title,
          'answer_content': answer_vote.answer.content
        }    
    
    serializer = UserReputationSerializer(reputations, many=True)
    return Response(serializer.data)