# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import F

from spirit.models import Comment
from ..comment import comment_post_update
from ..comment_like import comment_like_post_create, comment_like_post_delete
from ..topic_moderate import topic_post_moderate


def comment_post_update_handler(sender, comment, **kwargs):
    Comment.objects.filter(pk=comment.pk).update(modified_count=F('modified_count') + 1)


def comment_like_post_create_handler(sender, comment, **kwargs):
    Comment.objects.filter(pk=comment.pk).update(likes_count=F('likes_count') + 1)


def comment_like_post_delete_handler(sender, comment, **kwargs):
    Comment.objects.filter(pk=comment.pk).update(likes_count=F('likes_count') - 1)


def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
    Comment.objects.create(user=user, topic=topic, action=action, comment="action", comment_html="action")


comment_post_update.connect(comment_post_update_handler, dispatch_uid=__name__)
comment_like_post_create.connect(comment_like_post_create_handler, dispatch_uid=__name__)
comment_like_post_delete.connect(comment_like_post_delete_handler, dispatch_uid=__name__)
topic_post_moderate.connect(topic_post_moderate_handler, dispatch_uid=__name__)
