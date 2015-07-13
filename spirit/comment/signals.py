# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import F
from django.dispatch import Signal

from .models import Comment
from ..topic.moderate.signals import topic_post_moderate


comment_posted = Signal(providing_args=['comment', 'mentions'])
comment_moved = Signal(providing_args=['comments', 'topic_from'])





def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
    Comment.objects.create(user=user, topic=topic, action=action, comment="action", comment_html="action")


topic_post_moderate.connect(topic_post_moderate_handler, dispatch_uid=__name__)
