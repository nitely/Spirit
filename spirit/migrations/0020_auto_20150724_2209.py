# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0019_auto_20150724_2155'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='comment',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='user',
        ),
        migrations.AlterField(
            model_name='commentflag',
            name='comment',
            field=models.OneToOneField(to='spirit_comment.Comment'),
        ),
        migrations.AlterField(
            model_name='commenthistory',
            name='comment_fk',
            field=models.ForeignKey(verbose_name='original comment', to='spirit_comment.Comment'),
        ),
        migrations.AlterField(
            model_name='commentlike',
            name='comment',
            field=models.ForeignKey(related_name='comment_likes', to='spirit_comment.Comment'),
        ),
        migrations.AlterField(
            model_name='flag',
            name='comment',
            field=models.ForeignKey(to='spirit_comment.Comment'),
        ),
        migrations.AlterField(
            model_name='topicnotification',
            name='comment',
            field=models.ForeignKey(to='spirit_comment.Comment', blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
