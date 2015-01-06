# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import register
from spirit.models.comment_like import CommentLike
from spirit.forms.comment_like import LikeForm


@register.inclusion_tag('spirit/comment_like/_form.html')
def render_like_form(comment, like, next=None):
    form = LikeForm()
    return {'form': form, 'comment_id': comment.pk, 'like': like, 'next': next}


@register.simple_tag()
def populate_likes(comments, user, to_attr='like'):
    # TODO: remove
    # TODO: use Prefetch on django 1.7
    # move this to CustomQuerySet.as_manager
    # move this from template to view

    # user_likes = CommentLike.objects.filter(user=user)
    # prefetch = Prefetch("comment_likes", queryset=user_likes, to_attr=to_attr)
    # comments = comments.prefetch_related(prefetch)

    likes = CommentLike.objects.filter(comment__in=comments, user=user)
    likes_dict = {l.comment_id: l for l in likes}

    for c in comments:
        setattr(c, to_attr, likes_dict.get(c.pk))

    return ""
