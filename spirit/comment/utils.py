# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ..topic.notification.models import TopicNotification, UNDEFINED
from ..topic.unread.models import TopicUnread


def comment_posted(comment, mentions):
    # Todo test detail views
    TopicNotification.create_maybe(user=comment.user, comment=comment, action=UNDEFINED)
    TopicNotification.notify_new_comment(comment=comment)
    TopicNotification.notify_new_mentions(comment=comment, mentions=mentions)
    TopicUnread.unread_new_comment(comment=comment)
    comment.topic.increase_comment_count()