# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic_notification', '0003_auto_20150726_0203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicnotification',
            name='comment',
            field=models.ForeignKey(to='spirit_comment.Comment'),
        ),
    ]
