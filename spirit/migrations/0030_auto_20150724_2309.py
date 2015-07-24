# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0029_auto_20150724_2304'),
    ]

    state_operations = [
        migrations.AlterUniqueTogether(
            name='commentbookmark',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='commentbookmark',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='commentbookmark',
            name='user',
        ),
        migrations.DeleteModel(
            name='CommentBookmark',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
