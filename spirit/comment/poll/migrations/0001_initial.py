# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_comment', '0002_auto_20150828_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentPoll',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('title', models.CharField(max_length=255, blank=True, verbose_name='title')),
                ('choice_min', models.PositiveIntegerField(default=1, verbose_name='choice min')),
                ('choice_max', models.PositiveIntegerField(default=1, verbose_name='choice max')),
                ('voter_count', models.PositiveIntegerField(default=0, verbose_name='voter count')),
                ('close_at', models.DateTimeField(null=True, blank=True, verbose_name='auto close at')),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.ForeignKey(to='spirit_comment.Comment', related_name='comment_polls')),
            ],
            options={
                'ordering': ['-pk'],
                'verbose_name_plural': 'comments polls',
                'verbose_name': 'comment poll',
            },
        ),
        migrations.CreateModel(
            name='CommentPollChoice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('number', models.PositiveIntegerField(verbose_name='number')),
                ('description', models.CharField(max_length=255, verbose_name='choice description')),
                ('vote_count', models.PositiveIntegerField(default=0, verbose_name='vote count')),
                ('is_removed', models.BooleanField(default=False)),
                ('poll', models.ForeignKey(to='spirit_comment_poll.CommentPoll', related_name='poll_choices')),
            ],
            options={
                'ordering': ['number', '-pk'],
                'verbose_name_plural': 'poll choices',
                'verbose_name': 'poll choice',
            },
        ),
        migrations.CreateModel(
            name='CommentPollVote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('choice', models.ForeignKey(to='spirit_comment_poll.CommentPollChoice', related_name='choice_votes')),
                ('voter', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='st_cp_votes')),
            ],
            options={
                'ordering': ['-pk'],
                'verbose_name_plural': 'poll votes',
                'verbose_name': 'poll vote',
            },
        ),
        migrations.AlterUniqueTogether(
            name='commentpollvote',
            unique_together=set([('voter', 'choice')]),
        ),
        migrations.AlterUniqueTogether(
            name='commentpollchoice',
            unique_together=set([('poll', 'number')]),
        ),
        migrations.AlterUniqueTogether(
            name='commentpoll',
            unique_together=set([('comment', 'name')]),
        ),
    ]
