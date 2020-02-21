from letsdiscuss.users.models import User, UserMeta, UserReputation
from letsdiscuss.qna.models import *

from datetime import datetime
from django.db.models import Sum

class ReputationEngine(object):

  def __init__(self, instance, initiator):
    self.instance = instance
    self.initiator = initiator
    self.vote_scoring = {
      'QUSUP': 10,
      'QUSDN': -2,
      'ANSUP': 10
    }

  def update_score_user_meta(self, created_by):
    # compute overall score and update in usermeta
    total_score = UserReputation.objects.filter(user=created_by).aggregate(Sum('points'))
    total_score = total_score['points__sum']

    user_meta = UserMeta.objects.get(user=created_by)
    user_meta.score = total_score if total_score else 0
    user_meta.save()


  def create_score_question_upvote(self):
    # create userreputation
    reputation = UserReputation.objects.create(**{
      'user': self.instance.question.created_by,
      'points': self.vote_scoring['QUSUP'],
      'comment': '',
      'created_by': self.initiator,
      'created_on': datetime.now(),
      'category': 'QUSUP'
    })

    # update reputation in questionvote
    self.instance.reputation = reputation
    self.instance.save()

    # compute overall score and update in usermeta
    self.update_score_user_meta(created_by=self.instance.question.created_by)


  def delete_score_revoke_vote(self):
    self.instance.reputation.delete()
    # compute overall score and update in usermeta
    self.update_score_user_meta(created_by=self.instance.question.created_by)


  def create_score_question_downvote(self):
    # create userreputation
    reputation = UserReputation.objects.create(**{
      'user': self.instance.question.created_by,
      'points': self.vote_scoring['QUSDN'],
      'comment': '',
      'created_by': self.initiator,
      'created_on': datetime.now(),
      'category': 'QUSDN'
    })

    # update reputation in questionvote
    self.instance.reputation = reputation
    self.instance.save()

    # compute overall score and update in usermeta
    self.update_score_user_meta(created_by=self.instance.question.created_by)


  def create_score_answer_upvote(self):
    # create userreputation
    reputation = UserReputation.objects.create(**{
      'user': self.instance.answer.created_by,
      'points': self.vote_scoring['ANSUP'],
      'comment': '',
      'created_by': self.initiator,
      'created_on': datetime.now(),
      'category': 'ANSUP'
    })

    # update reputation in questionvote
    self.instance.reputation = reputation
    self.instance.save()

    # compute overall score and update in usermeta
    self.update_score_user_meta(created_by=self.instance.answer.created_by)    
    
  def delete_score_answer_revoke_vote(self):
    self.instance.reputation.delete()
    # compute overall score and update in usermeta
    self.update_score_user_meta(created_by=self.instance.answer.created_by)

    
