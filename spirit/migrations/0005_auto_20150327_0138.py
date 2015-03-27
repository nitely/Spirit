# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0004_topic_is_globally_pinned'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['title', 'pk'], 'verbose_name_plural': 'categories', 'verbose_name': 'category'},
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-date', '-pk'], 'verbose_name_plural': 'comments', 'verbose_name': 'comment'},
        ),
        migrations.AlterModelOptions(
            name='commentflag',
            options={'ordering': ['-date', '-pk'], 'verbose_name_plural': 'comments flags', 'verbose_name': 'comment flag'},
        ),
        migrations.AlterModelOptions(
            name='commenthistory',
            options={'ordering': ['-date', '-pk'], 'verbose_name_plural': 'comments history', 'verbose_name': 'comment history'},
        ),
        migrations.AlterModelOptions(
            name='commentlike',
            options={'ordering': ['-date', '-pk'], 'verbose_name_plural': 'likes', 'verbose_name': 'like'},
        ),
        migrations.AlterModelOptions(
            name='flag',
            options={'ordering': ['-date', '-pk'], 'verbose_name_plural': 'flags', 'verbose_name': 'flag'},
        ),
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ['-last_active', '-pk'], 'verbose_name_plural': 'topics', 'verbose_name': 'topic'},
        ),
        migrations.AlterModelOptions(
            name='topicfavorite',
            options={'ordering': ['-date', '-pk'], 'verbose_name_plural': 'favorites', 'verbose_name': 'favorite'},
        ),
        migrations.AlterModelOptions(
            name='topicnotification',
            options={'ordering': ['-date', '-pk'], 'verbose_name_plural': 'topics notification', 'verbose_name': 'topic notification'},
        ),
        migrations.AlterModelOptions(
            name='topicprivate',
            options={'ordering': ['-date', '-pk'], 'verbose_name_plural': 'private topics', 'verbose_name': 'private topic'},
        ),
        migrations.AlterModelOptions(
            name='topicunread',
            options={'ordering': ['-date', '-pk'], 'verbose_name_plural': 'topics unread', 'verbose_name': 'topic unread'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-date_joined', '-pk'], 'verbose_name_plural': 'users', 'verbose_name': 'user'},
        ),
        migrations.AddField(
            model_name='user',
            name='is_verified',
            field=models.BooleanField(help_text='Designates whether the user has verified his account by email or by other means. Un-select this to let the user activate his account.', default=False, verbose_name='verified'),
            preserve_default=True,
        ),
    ]
