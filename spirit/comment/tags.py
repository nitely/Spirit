# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext as _
from django.utils.html import mark_safe

from ..core.tags.registry import register
from .poll.utils.render import render_polls
from .forms import CommentForm
from .models import MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED


@register.inclusion_tag('spirit/comment/_form.html')
def render_comments_form(topic, next=None):
    form = CommentForm()
    return {'form': form, 'topic_id': topic.pk, 'next': next}


@register.simple_tag()
def get_comment_action_text(action):
    if action == MOVED:
        return _("This topic has been moved")
    elif action == CLOSED:
        return _("This topic has been closed")
    elif action == UNCLOSED:
        return _("This topic has been unclosed")
    elif action == PINNED:
        return _("This topic has been pinned")
    elif action == UNPINNED:
        return _("This topic has been unpinned")
    else:
        return _("Unknown topic moderation action")


@register.simple_tag(takes_context=True)
def post_render_comment(context, comment):
    request = context['request']
    csrf_token = context['csrf_token']
    return mark_safe(render_polls(comment, request, csrf_token))
