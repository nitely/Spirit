# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from spirit.models import CommentHistory
from ..comment import comment_pre_update, comment_post_update


def comment_pre_update_handler(sender, comment, **kwargs):
    # Save original comment
    exists = CommentHistory.objects.filter(comment_fk=comment).exists()

    if not exists:
        CommentHistory.objects.create(comment_fk=comment,
                                      comment_html=comment.comment_html,
                                      date=comment.date)


def comment_post_update_handler(sender, comment, **kwargs):
    CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)


comment_pre_update.connect(comment_pre_update_handler, dispatch_uid=__name__)
comment_post_update.connect(comment_post_update_handler, dispatch_uid=__name__)
