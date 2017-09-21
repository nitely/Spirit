# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ...comment import tags as comment
from ...comment.like import tags as comment_like
from ...search import tags as search
from ...topic.favorite import tags as topic_favorite
from ...topic.notification import tags as topic_notification
from ...topic.private import tags as topic_private
from ..tags import avatar
from ..tags import gravatar
from ..tags import messages
from ..tags import paginator
from ..tags import settings
from ..tags import social_share
from ..tags import time
from ..tags import urls
from ..tags.registry import register


__all__ = [
    'comment',
    'comment_like',
    'comment_poll',
    'search',
    'topic_favorite',
    'topic_notification',
    'topic_private',
    'avatar',
    'gravatar',
    'messages',
    'paginator',
    'settings',
    'social_share',
    'time',
    'urls',
    'register'
]
