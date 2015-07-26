# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def populate_comments_for_nulls(apps, schema_editor):
    TopicNotification = apps.get_model('spirit_topic_notification.TopicNotification')
    notifications = TopicNotification.objects.filter(comment=None)
    for n in notifications:
        TopicNotification.objects\
            .filter(pk=n.pk)\
            .update(comment=n.topic.comment_set.last(), action=0)


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic_notification', '0002_auto_20150724_2238'),
    ]

    operations = [
        migrations.RunPython(populate_comments_for_nulls),
    ]
