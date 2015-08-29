# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('spirit_comment', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentPoll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='name', max_length=255)),
                ('title', models.CharField(verbose_name='title', max_length=255)),
                ('choice_limit', models.PositiveIntegerField(verbose_name='choice limit', default=1)),
                ('is_closed', models.BooleanField(default=False)),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.ForeignKey(to='spirit_comment.Comment', related_name='comment_polls')),
            ],
            options={
                'verbose_name': 'comment poll',
                'verbose_name_plural': 'comments polls',
                'ordering': ['-pk'],
            },
        ),
        migrations.CreateModel(
            name='CommentPollChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('number', models.PositiveIntegerField(verbose_name='number')),
                ('description', models.CharField(verbose_name='choice description', max_length=255)),
                ('vote_count', models.PositiveIntegerField(verbose_name='vote count', default=0)),
                ('is_removed', models.BooleanField(default=False)),
                ('poll', models.ForeignKey(to='spirit_comment_poll.CommentPoll', related_name='poll_choices')),
            ],
            options={
                'verbose_name': 'poll choice',
                'verbose_name_plural': 'poll choices',
                'ordering': ['number', '-pk'],
            },
        ),
        migrations.CreateModel(
            name='CommentPollVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('choice', models.ForeignKey(to='spirit_comment_poll.CommentPollChoice', related_name='choice_votes')),
                ('voter', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='st_cp_votes')),
            ],
            options={
                'verbose_name': 'poll vote',
                'verbose_name_plural': 'poll votes',
                'ordering': ['-created_at', '-pk'],
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
