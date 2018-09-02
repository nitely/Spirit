# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic_unread', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topicunread',
            name='user',
            field=models.ForeignKey(related_name='st_topics_unread', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
