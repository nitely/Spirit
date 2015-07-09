# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from spirit.apps.comment import tags as comment
from spirit.apps.comment.like import tags as comment_like
from spirit.apps.search import tags as search
from spirit.apps.topic.favorite import tags as topic_favorite
from spirit.apps.topic.notification import tags as topic_notification
from spirit.apps.topic.poll import tags as topic_poll
from spirit.apps.topic.private import tags as topic_private
from ..tags import avatar
from ..tags import gravatar
from ..tags import messages
from ..tags import paginator
from ..tags import social_share
from ..tags import time
from ..tags.registry import register


__all__ = [
    'comment',
    'comment_like',
    'topic_poll',
    'search',
    'topic_favorite',
    'topic_notification',
    'topic_private',
    'avatar',
    'gravatar',
    'messages',
    'paginator',
    'social_share',
    'time',
    'register'
]
