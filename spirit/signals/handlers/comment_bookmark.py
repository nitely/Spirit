# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.db import IntegrityError

from spirit.models import CommentBookmark
from ..topic import topic_viewed


def topic_page_viewed_handler(sender, request, topic, **kwargs):
    if not request.user.is_authenticated():
        return

    try:
        page_number = int(request.GET.get(settings.ST_COMMENTS_PAGE_VAR, 1))
    except ValueError:
        return

    comment_number = settings.ST_COMMENTS_PER_PAGE * (page_number - 1) + 1

    try:
        CommentBookmark.objects.update_or_create(user=request.user, topic=topic,
                                                 defaults={'comment_number': comment_number, })
    except IntegrityError:
        pass


topic_viewed.connect(topic_page_viewed_handler, dispatch_uid=__name__)
