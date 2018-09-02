# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_topic', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TopicPoll',
            fields=[
                ('topic', models.OneToOneField(serialize=False, to='spirit_topic.Topic', verbose_name='topic', primary_key=True, related_name='poll', on_delete=models.CASCADE)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('choice_limit', models.PositiveIntegerField(default=1, verbose_name='choice limit')),
                ('is_closed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'topics polls',
                'verbose_name': 'topic poll',
            },
        ),
        migrations.CreateModel(
            name='TopicPollChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255, verbose_name='choice description')),
                ('vote_count', models.PositiveIntegerField(default=0, verbose_name='vote count')),
                ('poll', models.ForeignKey(to='spirit_topic_poll.TopicPoll', verbose_name='poll', related_name='choices', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'poll choices',
                'verbose_name': 'poll choice',
            },
        ),
        migrations.CreateModel(
            name='TopicPollVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('choice', models.ForeignKey(to='spirit_topic_poll.TopicPollChoice', verbose_name='poll choice', related_name='votes', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(verbose_name='voter', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'poll votes',
                'verbose_name': 'poll vote',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicpollvote',
            unique_together=set([('user', 'choice')]),
        ),
    ]
