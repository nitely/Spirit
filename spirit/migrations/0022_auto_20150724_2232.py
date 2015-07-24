# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0021_auto_20150724_2210'),
    ]

    state_operations = [
        migrations.AlterUniqueTogether(
            name='topicnotification',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='topicnotification',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='topicnotification',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='topicnotification',
            name='user',
        ),
        migrations.DeleteModel(
            name='TopicNotification',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
