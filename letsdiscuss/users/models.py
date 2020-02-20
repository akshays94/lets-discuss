import uuid
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
        UserMeta.objects.create(**{
          'user': instance
        })



class UserMeta(models.Model):
  user    = models.ForeignKey(User, on_delete=models.CASCADE)
  score   = models.IntegerField(default=0)
  tagline = models.CharField(max_length=128)

  def __str__(self):
    return 'id({id}) -> [P{score}] = {name}'.format(**{
      'name': self.user.username,
      'score': self.score,
      'id': self.id
    })



class UserReputation(models.Model):
  
  # Inspired from StackOverflow Reputation System
  REPUTATION_CATEGORIES = (
		('QUSUP', 'Question Upvote'),             # +10
		('ANSUP', 'Answer Upvote'),               # +10
		('ASAC1', 'Answer Accepted - Answerer'),  # +15
		('ASAC2', 'Answer Accepted - Acceptor'),  # +2
		('QUSDN', 'Question Downvote'),           # -2
		('ASDN1', 'Answer Downvote'),             # -2
		('ASDN2', 'Answer Downvote By Me'),       # -1
	)

  user          = models.ForeignKey(User, on_delete=models.CASCADE)
  points        = models.IntegerField(default=0)
  comment       = models.CharField(max_length=128)
  created_by    = models.ForeignKey(User, 
                  related_name='%(app_label)s_%(class)s_creator', 
                  on_delete=models.CASCADE)
  created_on    = models.DateTimeField(auto_now_add=True)
  category      = models.CharField(max_length=5,
										choices=REPUTATION_CATEGORIES, default='QUSUP')

  def __str__(self):
    return 'id({id}) -> [P{points}] = {name}'.format(**{
      'name': self.user.username,
      'points': self.points,
      'id': self.id
    })