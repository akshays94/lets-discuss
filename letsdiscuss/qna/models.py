from django.db import models
from letsdiscuss.users.models import User
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save

class BaseModel(models.Model):
    
    class Meta:
        abstract = True

    # objects			= BaseModelManager()
    created_by 		= models.ForeignKey(User, 
                            related_name='%(app_label)s_%(class)s_creator', 
                            on_delete=models.CASCADE)
    created_on 		= models.DateTimeField(auto_now_add=True)
    modified_by 	= models.ForeignKey(User, 
                            related_name='%(app_label)s_%(class)s_modifier', 
                            on_delete=models.CASCADE)
    modified_on		= models.DateTimeField(auto_now=True)
    deleted_by		= models.ForeignKey(User, null=True, blank=True, 
                            related_name='%(app_label)s_%(class)s_deleter', 
                            on_delete=models.CASCADE)
    deleted_on		= models.DateTimeField(null=True, blank=True)
    is_deleted		= models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
    
        if not self.id or not self.created_on:
            self.created_on = timezone.now()
    
        return super(BaseModel,	self).save(*args, **kwargs)



class Question(BaseModel):

    title       = models.CharField(max_length=1024)
    content     = models.TextField()
    votes       = models.IntegerField(default=0)

    def __str__(self):
        return '{id}: {title}'.format(**{
            'id': self.id,
            'title': self.title
        })



class QuestionVote(BaseModel):
    
    is_upvote   = models.BooleanField(default=True)
    question    = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return '{id}: qid[{qid}] | {title} <<- {vote} ({uname})'.format(**{
            'id': self.id,
            'qid': self.question_id,
            'title': self.question.title,
            'vote': '[UPVOTED]' if self.is_upvote else '[DOWNVOTED]',
            'uname': self.created_by.username
        })

@receiver(post_save, sender=QuestionVote)
def save_votes_count(sender, instance=None, created=False, **kwargs):
    if created or instance:
        upvotes = QuestionVote.objects.filter(question=instance.question, is_upvote=True).count()    
        downvotes = QuestionVote.objects.filter(question=instance.question, is_upvote=False).count()    
        instance.question.votes = upvotes - downvotes
        instance.question.save()


class Answer(BaseModel):

    question    = models.ForeignKey(Question, on_delete=models.CASCADE)
    content     = models.TextField()
    votes       = models.IntegerField(default=0)
    is_correct  = models.BooleanField(default=False)

    def __str__(self):
        return '{id}: qid[{qid}] | {content} {iscorrect}'.format(**{
            'id': self.id,
            'qid': self.question_id,
            'content': self.content,
            'iscorrect': '[CORRECT]' if self.is_correct else ''
        })


class AnswerVote(BaseModel):
    
    is_upvote   = models.BooleanField(default=True)
    answer      = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return '{id}: aid[{aid}] <<- {vote} ({uname})'.format(**{
            'id': self.id,
            'aid': self.answer_id,
            'vote': '[UPVOTED]' if self.is_upvote else '[DOWNVOTED]',
            'uname': self.created_by.username
        })

@receiver(post_save, sender=AnswerVote)
def save_answer_votes_count(sender, instance=None, created=False, **kwargs):
    if created or instance:
        upvotes = AnswerVote.objects.filter(answer=instance.answer, is_upvote=True).count()    
        downvotes = AnswerVote.objects.filter(answer=instance.answer, is_upvote=False).count()    
        instance.answer.votes = upvotes - downvotes
        instance.answer.save()        