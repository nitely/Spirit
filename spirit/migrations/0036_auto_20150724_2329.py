# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0035_auto_20150724_2321'),
    ]

    state_operations = [
        migrations.AlterUniqueTogether(
            name='commentlike',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='commentlike',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='commentlike',
            name='user',
        ),
        migrations.DeleteModel(
            name='CommentLike',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
