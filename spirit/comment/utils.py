# -*- coding: utf-8 -*-

from spirit.core import tasks
from spirit.topic.notification.models import TopicNotification
from spirit.topic.unread.models import TopicUnread
from .history.models import CommentHistory
from .poll.utils.render_static import post_render_static_polls


def comment_posted(comment, mentions):
    TopicNotification.create_maybe(
        user=comment.user,
        comment=comment,
        action=TopicNotification.UNDEFINED)
    TopicNotification.notify_new_comment(comment=comment)
    TopicNotification.notify_new_mentions(comment=comment, mentions=mentions)
    TopicUnread.unread_new_comment(comment=comment)
    comment.topic.increase_comment_count()
    tasks.search_index_update(topic_pk=comment.topic.pk)
    tasks.notify_reply(comment_id=comment.pk)
    if mentions:
        tasks.notify_mention(comment_id=comment.pk)


def pre_comment_update(comment):
    comment.comment_html = post_render_static_polls(comment)
    CommentHistory.create_maybe(comment)


def post_comment_update(comment):
    comment.increase_modified_count()

    comment.comment_html = post_render_static_polls(comment)
    CommentHistory.create(comment)


# XXX add tests
def post_comment_move(comment, topic):
    TopicNotification.sync(comment=comment, topic=topic)
