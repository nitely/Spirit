# -*- coding: utf-8 -*-

from ..notification.models import TopicNotification


def notify_access(user, topic_private):
    TopicNotification.create_maybe(
        user=user,
        comment=topic_private.topic.comment_set.last(),
        is_read=False
    )
