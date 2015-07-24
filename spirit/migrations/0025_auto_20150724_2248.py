# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def rename_model_content_type(apps, schema_editor):
    content_types = apps.get_model('contenttypes.ContentType')
    content_types.objects.filter(
        app_label='spirit', model='TopicPoll'.lower()
    ).update(app_label='spirit_topic_poll')
    content_types.objects.filter(
        app_label='spirit', model='TopicPollChoice'.lower()
    ).update(app_label='spirit_topic_poll')
    content_types.objects.filter(
        app_label='spirit', model='TopicPollVote'.lower()
    ).update(app_label='spirit_topic_poll')


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0024_auto_20150724_2248'),
    ]

    operations = [
        migrations.RunPython(rename_model_content_type),
    ]
