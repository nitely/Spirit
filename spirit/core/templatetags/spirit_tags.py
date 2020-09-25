# -*- coding: utf-8 -*-

from spirit.comment import tags as comment
from spirit.comment.like import tags as comment_like
from spirit.search import tags as search
from spirit.topic.favorite import tags as topic_favorite
from spirit.topic.notification import tags as topic_notification
from spirit.topic.private import tags as topic_private
from spirit.core.tags import avatar
from spirit.core.tags import messages
from spirit.core.tags import paginator
from spirit.core.tags import settings
from spirit.core.tags import social_share
from spirit.core.tags import time
from spirit.core.tags import urls
from spirit.core.tags.registry import register


__all__ = [
    'comment',
    'comment_like',
    'search',
    'topic_favorite',
    'topic_notification',
    'topic_private',
    'avatar',
    'messages',
    'paginator',
    'settings',
    'social_share',
    'time',
    'urls',
    'register'
]
