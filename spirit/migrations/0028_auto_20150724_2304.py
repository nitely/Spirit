# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0027_auto_20150724_2256'),
    ]

    state_operations = [
        migrations.AlterUniqueTogether(
            name='topicunread',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='topicunread',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='topicunread',
            name='user',
        ),
        migrations.DeleteModel(
            name='TopicUnread',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
