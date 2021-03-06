# Generated by Django 3.0.2 on 2020-02-20 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_usermeta_tagline'),
    ]

    operations = [
        migrations.AddField(
            model_name='userreputation',
            name='category',
            field=models.CharField(choices=[('QUSUP', 'Question Upvote'), ('ANSUP', 'Answer Upvote'), ('ASAC1', 'Answer Accepted - Answerer'), ('ASAC2', 'Answer Accepted - Acceptor'), ('QUSDN', 'Question Downvote'), ('ASDN1', 'Answer Downvote'), ('ASDN2', 'Answer Downvote By Me')], default='QUSUP', max_length=5),
        ),
    ]
