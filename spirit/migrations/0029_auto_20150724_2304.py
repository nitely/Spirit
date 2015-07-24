# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def rename_model_content_type(apps, schema_editor):
    content_types = apps.get_model('contenttypes.ContentType')
    content_types.objects.filter(
        app_label='spirit', model='TopicUnread'.lower()
    ).update(app_label='spirit_topic_unread')


class Migration(migrations.Migration):

    dependencies = [
        ('spirit', '0028_auto_20150724_2304'),
    ]

    operations = [
        migrations.RunPython(rename_model_content_type),
    ]
