# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic', '0002_auto_20150724_2106'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit', '0024_auto_20150724_2248')
    ]

    state_operations = [
        migrations.CreateModel(
            name='TopicPoll',
            fields=[
                ('topic', models.OneToOneField(verbose_name='topic', related_name='poll', serialize=False, to='spirit_topic.Topic', primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('choice_limit', models.PositiveIntegerField(verbose_name='choice limit', default=1)),
                ('is_closed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name_plural': 'topics polls',
                'verbose_name': 'topic poll',
                'db_table': 'spirit_poll_topicpoll',
            },
        ),
        migrations.CreateModel(
            name='TopicPollChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('description', models.CharField(max_length=255, verbose_name='choice description')),
                ('vote_count', models.PositiveIntegerField(verbose_name='vote count', default=0)),
                ('poll', models.ForeignKey(verbose_name='poll', related_name='choices', to='spirit_topic_poll.TopicPoll')),
            ],
            options={
                'verbose_name_plural': 'poll choices',
                'verbose_name': 'poll choice',
                'db_table': 'spirit_poll_topicpollchoice',
            },
        ),
        migrations.CreateModel(
            name='TopicPollVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('choice', models.ForeignKey(verbose_name='poll choice', related_name='votes', to='spirit_topic_poll.TopicPollChoice')),
                ('user', models.ForeignKey(verbose_name='voter', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'poll votes',
                'verbose_name': 'poll vote',
                'db_table': 'spirit_poll_topicpollvote',
            },
        ),
        migrations.AlterUniqueTogether(
            name='topicpollvote',
            unique_together=set([('user', 'choice')]),
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
