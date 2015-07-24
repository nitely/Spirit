# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0023_auto_20150724_2234'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='topicpoll',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='topicpollchoice',
            name='poll',
        ),
        migrations.AlterUniqueTogether(
            name='topicpollvote',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='topicpollvote',
            name='choice',
        ),
        migrations.RemoveField(
            model_name='topicpollvote',
            name='user',
        ),
        migrations.DeleteModel(
            name='TopicPoll',
        ),
        migrations.DeleteModel(
            name='TopicPollChoice',
        ),
        migrations.DeleteModel(
            name='TopicPollVote',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
