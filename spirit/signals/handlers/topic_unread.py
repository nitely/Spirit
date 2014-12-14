# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils import timezone
from django.db import IntegrityError

from spirit.models import TopicUnread
from ..comment import comment_posted
from ..topic import topic_viewed


def topic_page_viewed_handler(sender, request, topic, **kwargs):
    if not request.user.is_authenticated():
        return

    try:
        TopicUnread.objects.update_or_create(user=request.user, topic=topic,
                                             defaults={'is_read': True, })
    except IntegrityError:
        pass


def comment_posted_handler(sender, comment, **kwargs):
    TopicUnread.objects.filter(topic=comment.topic)\
        .exclude(user=comment.user)\
        .update(is_read=False, date=timezone.now())


topic_viewed.connect(topic_page_viewed_handler, dispatch_uid=__name__)
comment_posted.connect(comment_posted_handler, dispatch_uid=__name__)
