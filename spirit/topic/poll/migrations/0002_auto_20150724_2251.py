# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic_poll', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='topicpoll',
            table=None,
        ),
        migrations.AlterModelTable(
            name='topicpollchoice',
            table=None,
        ),
        migrations.AlterModelTable(
            name='topicpollvote',
            table=None,
        ),
    ]
