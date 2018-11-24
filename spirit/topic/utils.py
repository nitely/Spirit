# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ..comment.bookmark.models import CommentBookmark
from .notification.models import TopicNotification
from .unread.models import TopicUnread


def topic_viewed(request, topic):
    # Todo test detail views
    user = request.user
    CommentBookmark.increase_or_create(
        user=user,
        topic=topic,
        comment_number=CommentBookmark.page_to_comment_number(
            request.GET.get('page', 1)))
    TopicNotification.mark_as_read(user=user, topic=topic)
    TopicUnread.create_or_mark_as_read(user=user, topic=topic)
    topic.increase_view_count()
