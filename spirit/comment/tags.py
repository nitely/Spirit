# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe

from ..core.conf import settings
from ..core.tags.registry import register
from .poll.utils.render import render_polls
from .forms import CommentForm
from .models import MOVED, CLOSED, UNCLOSED, PINNED, UNPINNED


@register.inclusion_tag('spirit/comment/_form.html')
def render_comments_form(topic, next=None):
    form = CommentForm()
    return {
        'form': form,
        'topic_id': topic.pk,
        'next': next,
    }


@register.simple_tag()
def get_allowed_file_types():
    return ", ".join(
        '.%s' % ext
        for ext in sorted(settings.ST_ALLOWED_UPLOAD_FILE_MEDIA_TYPE.keys()))


@register.simple_tag()
def get_allowed_image_types():
    return ", ".join(
        '.%s' % ext
        for ext in sorted(settings.ST_ALLOWED_UPLOAD_IMAGE_FORMAT))


ACTIONS = {
    MOVED: _("This topic has been moved"),
    CLOSED: _("This topic has been closed"),
    UNCLOSED: _("This topic has been unclosed"),
    PINNED: _("This topic has been pinned"),
    UNPINNED: _("This topic has been unpinned")}


@register.simple_tag()
def get_comment_action_text(action):
    return ACTIONS.get(action, _("Unknown topic moderation action"))


@register.simple_tag(takes_context=True)
def post_render_comment(context, comment):
    request = context['request']
    csrf_token = context['csrf_token']
    return mark_safe(render_polls(comment, request, csrf_token))
