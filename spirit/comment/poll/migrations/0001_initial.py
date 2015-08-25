# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentPoll',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('choice_limit', models.PositiveIntegerField(verbose_name='choice limit', default=1)),
                ('is_closed', models.BooleanField(default=False)),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.ForeignKey(related_name='polls', to='spirit_comment.Comment')),
            ],
            options={
                'verbose_name_plural': 'comments polls',
                'verbose_name': 'comment poll',
                'ordering': ['-pk'],
            },
        ),
        migrations.CreateModel(
            name='CommentPollChoice',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('number', models.PositiveIntegerField(verbose_name='number')),
                ('description', models.CharField(max_length=255, verbose_name='choice description')),
                ('vote_count', models.PositiveIntegerField(verbose_name='vote count', default=0)),
                ('is_removed', models.BooleanField(default=False)),
                ('poll', models.ForeignKey(related_name='choices', verbose_name='poll', to='spirit_comment_poll.CommentPoll')),
            ],
            options={
                'verbose_name_plural': 'poll choices',
                'verbose_name': 'poll choice',
                'ordering': ['-pk'],
            },
        ),
        migrations.CreateModel(
            name='CommentPollVote',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('choice', models.ForeignKey(related_name='votes', verbose_name='poll choice', to='spirit_comment_poll.CommentPollChoice')),
                ('voter', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='voter')),
            ],
            options={
                'verbose_name_plural': 'poll votes',
                'verbose_name': 'poll vote',
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
