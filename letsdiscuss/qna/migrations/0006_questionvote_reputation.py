# Generated by Django 3.0.2 on 2020-02-21 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_userreputation_category'),
        ('qna', '0005_answer_is_correct'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionvote',
            name='reputation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='users.UserReputation'),
            preserve_default=False,
        ),
    ]