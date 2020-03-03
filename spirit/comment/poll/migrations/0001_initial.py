# -*- coding: utf-8 -*-
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='name', max_length=255)),
                ('title', models.CharField(verbose_name='title', blank=True, max_length=255)),
                ('choice_min', models.PositiveIntegerField(default=1, verbose_name='choice min')),
                ('choice_max', models.PositiveIntegerField(default=1, verbose_name='choice max')),
                ('mode', models.IntegerField(choices=[(0, 'default'), (1, 'secret')], default=0, verbose_name='mode')),
                ('close_at', models.DateTimeField(verbose_name='auto close at', blank=True, null=True)),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('comment', models.ForeignKey(to='spirit_comment.Comment', related_name='comment_polls', on_delete=models.CASCADE)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('number', models.PositiveIntegerField(verbose_name='number')),
                ('description', models.CharField(verbose_name='choice description', max_length=255)),
                ('vote_count', models.PositiveIntegerField(default=0, verbose_name='vote count')),
                ('is_removed', models.BooleanField(default=False)),
                ('poll', models.ForeignKey(to='spirit_comment_poll.CommentPoll', related_name='poll_choices', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'poll choices',
                'verbose_name': 'poll choice',
                'ordering': ['number', '-pk'],
            },
        ),
        migrations.CreateModel(
            name='CommentPollVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('choice', models.ForeignKey(to='spirit_comment_poll.CommentPollChoice', related_name='choice_votes', on_delete=models.CASCADE)),
                ('voter', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='st_cp_votes', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name_plural': 'poll votes',
                'verbose_name': 'poll vote',
                'ordering': ['-pk'],
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
