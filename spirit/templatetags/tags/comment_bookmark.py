#-*- coding: utf-8 -*-

from . import register
from spirit.models.comment_bookmark import CommentBookmark


@register.simple_tag()
def populate_bookmarks(topics, user, to_attr='bookmark'):
    bookmarks = CommentBookmark.objects.filter(topic__in=topics, user=user)\
        .select_related('topic')
    bookmarks_dict = {b.topic_id: b for b in bookmarks}

    for t in topics:
        setattr(t, to_attr, bookmarks_dict.get(t.pk))

    return ""