# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentPoll',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
                'ordering': ['-pk'],
                'verbose_name_plural': 'comments polls',
            },
        ),
        migrations.CreateModel(
            name='CommentPollChoice',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('number', models.PositiveIntegerField(verbose_name='number')),
                ('description', models.CharField(verbose_name='choice description', max_length=255)),
                ('vote_count', models.PositiveIntegerField(verbose_name='vote count', default=0)),
                ('is_removed', models.BooleanField(default=False)),
                ('poll', models.ForeignKey(to='spirit_comment_poll.CommentPoll', related_name='poll_choices')),
            ],
            options={
                'verbose_name': 'poll choice',
                'ordering': ['-pk'],
                'verbose_name_plural': 'poll choices',
            },
        ),
        migrations.CreateModel(
            name='CommentPollVote',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('choice', models.ForeignKey(to='spirit_comment_poll.CommentPollChoice', related_name='choice_votes')),
                ('voter', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='st_cp_votes')),
            ],
            options={
                'verbose_name': 'poll vote',
                'ordering': ['-created_at', '-pk'],
                'verbose_name_plural': 'poll votes',
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
