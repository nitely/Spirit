# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0031_auto_20150724_2309'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='commentflag',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='commentflag',
            name='moderator',
        ),
        migrations.AlterUniqueTogether(
            name='flag',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='flag',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='flag',
            name='user',
        ),
        migrations.DeleteModel(
            name='CommentFlag',
        ),
        migrations.DeleteModel(
            name='Flag',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
