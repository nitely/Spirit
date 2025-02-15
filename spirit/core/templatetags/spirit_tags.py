from spirit.comment import tags as comment
from spirit.comment.like import tags as comment_like
from spirit.core.tags import (
    avatar,
    messages,
    paginator,
    settings,
    social_share,
    time,
    urls,
)
from spirit.core.tags.registry import register
from spirit.search import tags as search
from spirit.topic.favorite import tags as topic_favorite
from spirit.topic.notification import tags as topic_notification
from spirit.topic.private import tags as topic_private

__all__ = [
    "comment",
    "comment_like",
    "search",
    "topic_favorite",
    "topic_notification",
    "topic_private",
    "avatar",
    "messages",
    "paginator",
    "settings",
    "social_share",
    "time",
    "urls",
    "register",
]
