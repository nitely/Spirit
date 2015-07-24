# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0017_auto_20150724_2104'),
    ]

    state_operations = [
        migrations.AlterUniqueTogether(
            name='topicfavorite',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='topicfavorite',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='topicfavorite',
            name='user',
        ),
        migrations.DeleteModel(
            name='TopicFavorite',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
