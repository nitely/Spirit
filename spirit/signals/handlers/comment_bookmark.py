# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from djconfig import config

from ...models.comment_bookmark import CommentBookmark
from ..topic import topic_viewed


def topic_page_viewed_handler(sender, request, topic, **kwargs):
    if not request.user.is_authenticated():
        return

    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        return

    comment_number = config.comments_per_page * (page_number - 1) + 1

    CommentBookmark.objects.update_or_create(user=request.user, topic=topic,
                                             defaults={'comment_number': comment_number, })


topic_viewed.connect(topic_page_viewed_handler, dispatch_uid=__name__)
