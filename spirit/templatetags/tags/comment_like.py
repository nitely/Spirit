# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from . import register
from ...forms.comment_like import LikeForm


@register.inclusion_tag('spirit/comment_like/_form.html')
def render_like_form(comment, like, next=None):
    form = LikeForm()
    return {'form': form, 'comment_id': comment.pk, 'like': like, 'next': next}
