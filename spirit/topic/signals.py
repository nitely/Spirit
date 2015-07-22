# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import F
from django.utils import timezone

from .models import Topic
from ..comment.signals import comment_moved


def comment_moved_handler(sender, comments, topic_from, **kwargs):
    Topic.objects.filter(pk=topic_from.pk)\
        .update(comment_count=F('comment_count') - len(comments))


comment_moved.connect(comment_moved_handler, dispatch_uid=__name__)