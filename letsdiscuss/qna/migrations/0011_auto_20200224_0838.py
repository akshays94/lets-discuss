# Generated by Django 3.0.2 on 2020-02-24 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_userreputation_category'),
        ('qna', '0010_answervote_downvote_reputation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answervote',
            name='downvote_reputation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='downvote_reputation', to='users.UserReputation'),
        ),
        migrations.AlterField(
            model_name='answervote',
            name='reputation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vote_reputation', to='users.UserReputation'),
        ),
    ]
