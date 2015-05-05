# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0009_auto_20150330_0858'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='category',
            table='spirit_category_category',
        ),
        migrations.AlterModelTable(
            name='comment',
            table='spirit_comment_comment',
        ),
        migrations.AlterModelTable(
            name='commentbookmark',
            table='spirit_bookmark_commentbookmark',
        ),
        migrations.AlterModelTable(
            name='commentflag',
            table='spirit_flag_commentflag',
        ),
        migrations.AlterModelTable(
            name='commenthistory',
            table='spirit_history_commenthistory',
        ),
        migrations.AlterModelTable(
            name='commentlike',
            table='spirit_like_commentlike',
        ),
        migrations.AlterModelTable(
            name='flag',
            table='spirit_flag_flag',
        ),
        migrations.AlterModelTable(
            name='topic',
            table='spirit_topic_topic',
        ),
        migrations.AlterModelTable(
            name='topicfavorite',
            table='spirit_favorite_topicfavorite',
        ),
        migrations.AlterModelTable(
            name='topicnotification',
            table='spirit_notification_topicnotification',
        ),
        migrations.AlterModelTable(
            name='topicpoll',
            table='spirit_poll_topicpoll',
        ),
        migrations.AlterModelTable(
            name='topicpollchoice',
            table='spirit_poll_topicpollchoice',
        ),
        migrations.AlterModelTable(
            name='topicpollvote',
            table='spirit_poll_topicpollvote',
        ),
        migrations.AlterModelTable(
            name='topicprivate',
            table='spirit_private_topicprivate',
        ),
        migrations.AlterModelTable(
            name='topicunread',
            table='spirit_unread_topicunread',
        ),
        migrations.AlterModelTable(
            name='user',
            table='spirit_user_user',
        ),
        migrations.AlterModelTable(
            name='userprofile',
            table='spirit_user_userprofile',
        ),
    ]
