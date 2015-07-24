# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0025_auto_20150724_2248'),
    ]

    state_operations = [
        migrations.AlterUniqueTogether(
            name='topicprivate',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='topicprivate',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='topicprivate',
            name='user',
        ),
        migrations.DeleteModel(
            name='TopicPrivate',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
