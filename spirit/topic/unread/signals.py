# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils import timezone

from .models import TopicUnread
from ...comment.signals import comment_posted





def comment_posted_handler(sender, comment, **kwargs):
    TopicUnread.objects.filter(topic=comment.topic)\
        .exclude(user=comment.user)\
        .update(is_read=False, date=timezone.now())


comment_posted.connect(comment_posted_handler, dispatch_uid=__name__)
