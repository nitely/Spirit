# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def forwards(apps, schema_editor):
    Topic = apps.get_model("spirit_topic", "Topic")
    for topic in Topic.objects.all():
        last_comment = topic.comment_set.filter(is_removed=False).first()
        if last_comment:
            topic.last_commenter = last_comment.user
            topic.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_topic', '0003_topic_last_commenter'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=noop),
    ]
