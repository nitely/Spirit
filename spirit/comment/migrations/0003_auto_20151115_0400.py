# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


# todo: remove in Spirit 0.5

def render_comments(apps, schema_editor):
    # This is due to a changes in the emoji renderer (images -> css) and no-follow links
    from ...core.utils.markdown import Markdown

    Comment = apps.get_model("spirit_comment", "Comment")

    for comment in Comment.objects.all():
        comment.comment_html = Markdown().render(comment.comment)
        comment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('spirit_comment', '0002_auto_20150828_2003'),
    ]

    operations = [
        migrations.RunPython(render_comments),
    ]
