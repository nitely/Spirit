# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0033_auto_20150724_2316'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='commenthistory',
            name='comment_fk',
        ),
        migrations.DeleteModel(
            name='CommentHistory',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
