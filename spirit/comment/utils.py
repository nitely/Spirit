# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ..topic.notification.models import TopicNotification


def comment_posted(comment, mentions):
    # Todo test detail views
    TopicNotification.create_maybe(user=comment.user, topic=comment.topic)
    TopicNotification.notify_new_comment(comment=comment)
    TopicNotification.notify_new_mentions(comment=comment, mentions=mentions)