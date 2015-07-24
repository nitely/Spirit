# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0015_auto_20150724_1940'),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name='topic',
            name='category',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='user',
        ),
        migrations.AlterField(
            model_name='comment',
            name='topic',
            field=models.ForeignKey(to='spirit_topic.Topic'),
        ),
        migrations.AlterField(
            model_name='commentbookmark',
            name='topic',
            field=models.ForeignKey(to='spirit_topic.Topic'),
        ),
        migrations.AlterField(
            model_name='topicfavorite',
            name='topic',
            field=models.ForeignKey(to='spirit_topic.Topic'),
        ),
        migrations.AlterField(
            model_name='topicnotification',
            name='topic',
            field=models.ForeignKey(to='spirit_topic.Topic'),
        ),
        migrations.AlterField(
            model_name='topicpoll',
            name='topic',
            field=models.OneToOneField(to='spirit_topic.Topic', related_name='poll', primary_key=True, verbose_name='topic', serialize=False),
        ),
        migrations.AlterField(
            model_name='topicprivate',
            name='topic',
            field=models.ForeignKey(related_name='topics_private', to='spirit_topic.Topic'),
        ),
        migrations.AlterField(
            model_name='topicunread',
            name='topic',
            field=models.ForeignKey(to='spirit_topic.Topic'),
        ),
        migrations.DeleteModel(
            name='Topic',
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=state_operations)
    ]
