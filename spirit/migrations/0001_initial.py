# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import spirit.utils.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=75, verbose_name='title')),
                ('slug', spirit.utils.models.AutoSlugField(db_index=False, populate_from='title', blank=True)),
                ('description', models.CharField(max_length=255, verbose_name='description', blank=True)),
                ('is_closed', models.BooleanField(default=False, verbose_name='closed')),
                ('is_removed', models.BooleanField(default=False, verbose_name='removed')),
                ('is_private', models.BooleanField(default=False, verbose_name='private')),
                ('parent', models.ForeignKey(verbose_name='category parent', blank=True, to='spirit.Category', null=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(max_length=3000, verbose_name='comment')),
                ('comment_html', models.TextField(verbose_name='comment html')),
                ('action', models.IntegerField(default=0, verbose_name='action', choices=[(0, 'comment'), (1, 'topic moved'), (2, 'topic closed'), (3, 'topic unclosed'), (4, 'topic pinned'), (5, 'topic unpinned')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_removed', models.BooleanField(default=False)),
                ('is_modified', models.BooleanField(default=False)),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True)),
                ('modified_count', models.PositiveIntegerField(default=0, verbose_name='modified count')),
                ('likes_count', models.PositiveIntegerField(default=0, verbose_name='likes count')),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommentBookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment_number', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'comment bookmark',
                'verbose_name_plural': 'comments bookmarks',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommentFlag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_closed', models.BooleanField(default=False)),
                ('comment', models.OneToOneField(to='spirit.Comment')),
                ('moderator', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'comment flag',
                'verbose_name_plural': 'comments flags',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommentHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment_html', models.TextField(verbose_name='comment html')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('comment_fk', models.ForeignKey(verbose_name='original comment', to='spirit.Comment')),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'comment history',
                'verbose_name_plural': 'comments history',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('comment', models.ForeignKey(related_name='comment_likes', to='spirit.Comment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'like',
                'verbose_name_plural': 'likes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('reason', models.IntegerField(verbose_name='reason', choices=[(0, 'Spam'), (1, 'Other')])),
                ('body', models.TextField(verbose_name='body', blank=True)),
                ('comment', models.ForeignKey(to='spirit.Comment')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'flag',
                'verbose_name_plural': 'flags',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ForumProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.CharField(max_length=75, verbose_name='location', blank=True)),
                ('last_seen', models.DateTimeField(auto_now=True, verbose_name='last seen')),
                ('last_ip', models.GenericIPAddressField(null=True, verbose_name='last ip', blank=True)),
                ('timezone', models.CharField(default='UTC', max_length=32, verbose_name='time zone', choices=[('Etc/GMT+12', '(GMT -12:00) Eniwetok, Kwajalein'), ('Etc/GMT+11', '(GMT -11:00) Midway Island, Samoa'), ('Etc/GMT+10', '(GMT -10:00) Hawaii'), ('Pacific/Marquesas', '(GMT -9:30) Marquesas Islands'), ('Etc/GMT+9', '(GMT -9:00) Alaska'), ('Etc/GMT+8', '(GMT -8:00) Pacific Time (US & Canada)'), ('Etc/GMT+7', '(GMT -7:00) Mountain Time (US & Canada)'), ('Etc/GMT+6', '(GMT -6:00) Central Time (US & Canada), Mexico City'), ('Etc/GMT+5', '(GMT -5:00) Eastern Time (US & Canada), Bogota, Lima'), ('America/Caracas', '(GMT -4:30) Venezuela'), ('Etc/GMT+4', '(GMT -4:00) Atlantic Time (Canada), Caracas, La Paz'), ('Etc/GMT+3', '(GMT -3:00) Brazil, Buenos Aires, Georgetown'), ('Etc/GMT+2', '(GMT -2:00) Mid-Atlantic'), ('Etc/GMT+1', '(GMT -1:00) Azores, Cape Verde Islands'), ('UTC', '(GMT) Western Europe Time, London, Lisbon, Casablanca'), ('Etc/GMT-1', '(GMT +1:00) Brussels, Copenhagen, Madrid, Paris'), ('Etc/GMT-2', '(GMT +2:00) Kaliningrad, South Africa'), ('Etc/GMT-3', '(GMT +3:00) Baghdad, Riyadh, Moscow, St. Petersburg'), ('Etc/GMT-4', '(GMT +4:00) Abu Dhabi, Muscat, Baku, Tbilisi'), ('Asia/Kabul', '(GMT +4:30) Afghanistan'), ('Etc/GMT-5', '(GMT +5:00) Ekaterinburg, Islamabad, Karachi, Tashkent'), ('Asia/Kolkata', '(GMT +5:30) India, Sri Lanka'), ('Asia/Kathmandu', '(GMT +5:45) Nepal'), ('Etc/GMT-6', '(GMT +6:00) Almaty, Dhaka, Colombo'), ('Indian/Cocos', '(GMT +6:30) Cocos Islands, Myanmar'), ('Etc/GMT-7', '(GMT +7:00) Bangkok, Hanoi, Jakarta'), ('Etc/GMT-8', '(GMT +8:00) Beijing, Perth, Singapore, Hong Kong'), ('Australia/Eucla', '(GMT +8:45) Australia (Eucla)'), ('Etc/GMT-9', '(GMT +9:00) Tokyo, Seoul, Osaka, Sapporo, Yakutsk'), ('Australia/North', '(GMT +9:30) Australia (Northern Territory)'), ('Etc/GMT-10', '(GMT +10:00) Eastern Australia, Guam, Vladivostok'), ('Etc/GMT-11', '(GMT +11:00) Magadan, Solomon Islands, New Caledonia'), ('Pacific/Norfolk', '(GMT +11:30) Norfolk Island'), ('Etc/GMT-12', '(GMT +12:00) Auckland, Wellington, Fiji, Kamchatka')])),
                ('is_administrator', models.BooleanField(default=False, verbose_name='administrator status')),
                ('is_moderator', models.BooleanField(default=False, verbose_name='moderator status')),
                ('topic_count', models.PositiveIntegerField(default=0, verbose_name='topic count')),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='comment count')),
                ('user', models.OneToOneField(related_name='forum_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'forum profile',
                'verbose_name_plural': 'forum profiles',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=75, verbose_name='title')),
                ('slug', spirit.utils.models.AutoSlugField(db_index=False, populate_from='title', blank=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('last_active', models.DateTimeField(auto_now_add=True, verbose_name='last active')),
                ('is_pinned', models.BooleanField(default=False, verbose_name='pinned')),
                ('is_closed', models.BooleanField(default=False, verbose_name='closed')),
                ('is_removed', models.BooleanField(default=False)),
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='views count')),
                ('comment_count', models.PositiveIntegerField(default=0, verbose_name='comment count')),
            ],
            options={
                'ordering': ['-last_active'],
                'verbose_name': 'topic',
                'verbose_name_plural': 'topics',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicFavorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'favorite',
                'verbose_name_plural': 'favorites',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('action', models.IntegerField(default=0, choices=[(0, 'Undefined'), (1, 'Mention'), (2, 'Comment')])),
                ('is_read', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('comment', models.ForeignKey(blank=True, to='spirit.Comment', null=True)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'topic notification',
                'verbose_name_plural': 'topics notification',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicPoll',
            fields=[
                ('topic', models.OneToOneField(related_name='poll', primary_key=True, serialize=False, to='spirit.Topic', verbose_name='topic')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('choice_limit', models.PositiveIntegerField(default=1, verbose_name='choice limit')),
                ('is_closed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'topic poll',
                'verbose_name_plural': 'topics polls',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicPollChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=255, verbose_name='choice description')),
                ('vote_count', models.PositiveIntegerField(default=0, verbose_name='vote count')),
                ('poll', models.ForeignKey(related_name='choices', verbose_name='poll', to='spirit.TopicPoll')),
            ],
            options={
                'verbose_name': 'poll choice',
                'verbose_name_plural': 'poll choices',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicPollVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('choice', models.ForeignKey(related_name='votes', verbose_name='poll choice', to='spirit.TopicPollChoice')),
                ('user', models.ForeignKey(verbose_name='voter', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'poll vote',
                'verbose_name_plural': 'poll votes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicPrivate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('topic', models.ForeignKey(related_name='topics_private', to='spirit.Topic')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'private topic',
                'verbose_name_plural': 'private topics',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TopicUnread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=True)),
                ('topic', models.ForeignKey(to='spirit.Topic')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
                'verbose_name': 'topic unread',
                'verbose_name_plural': 'topics unread',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='topicunread',
            unique_together=set([('user', 'topic')]),
        ),
        migrations.AlterUniqueTogether(
            name='topicprivate',
            unique_together=set([('user', 'topic')]),
        ),
        migrations.AlterUniqueTogether(
            name='topicpollvote',
            unique_together=set([('user', 'choice')]),
        ),
        migrations.AddField(
            model_name='topicnotification',
            name='topic',
            field=models.ForeignKey(to='spirit.Topic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topicnotification',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='topicnotification',
            unique_together=set([('user', 'topic')]),
        ),
        migrations.AddField(
            model_name='topicfavorite',
            name='topic',
            field=models.ForeignKey(to='spirit.Topic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topicfavorite',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='topicfavorite',
            unique_together=set([('user', 'topic')]),
        ),
        migrations.AddField(
            model_name='topic',
            name='category',
            field=models.ForeignKey(verbose_name='category', to='spirit.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topic',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='flag',
            unique_together=set([('user', 'comment')]),
        ),
        migrations.AlterUniqueTogether(
            name='commentlike',
            unique_together=set([('user', 'comment')]),
        ),
        migrations.AddField(
            model_name='commentbookmark',
            name='topic',
            field=models.ForeignKey(to='spirit.Topic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='commentbookmark',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='commentbookmark',
            unique_together=set([('user', 'topic')]),
        ),
        migrations.AddField(
            model_name='comment',
            name='topic',
            field=models.ForeignKey(to='spirit.Topic'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
