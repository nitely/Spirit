# -*- coding: utf-8 -*-

from ..apps.comment import tags as comment
from ..apps.comment.like import tags as comment_like
from ..apps.search import tags as search
from ..apps.topic.favorite import tags as topic_favorite
from ..apps.topic.notification import tags as topic_notification
from ..apps.topic.poll import tags as topic_poll
from ..apps.topic.private import tags as topic_private
from ..utils.tags import avatar
from ..utils.tags import gravatar
from ..utils.tags import messages
from ..utils.tags import paginator
from ..utils.tags import social_share
from ..utils.tags import time
from .registry import register


__all__ = [
    'comment', 'comment_like', 'topic_poll', 'search',
    'topic_favorite', 'topic_notification', 'topic_private', 'avatar',
    'gravatar', 'messages', 'paginator', 'social_share', 'time', 'register'
]
