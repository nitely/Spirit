# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe, format_html
from django.contrib.humanize.templatetags import humanize
from django.template.defaultfilters import date as date_format

from spirit.core.conf import settings
from spirit.core.tags.registry import register
from .poll.utils.render import render_polls
from .forms import CommentForm
from .models import Comment


@register.inclusion_tag('spirit/comment/_form.html', takes_context=True)
def render_comments_form(context, topic, next=None):
    form = CommentForm()
    return {
        'form': form,
        'topic_id': topic.pk,
        'next': next,
        # fixes #249
        'user': context['request'].user,
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
    Comment.MOVED: _("{user} moved this {time_ago}"),
    Comment.CLOSED: _("{user} closed this {time_ago}"),
    Comment.UNCLOSED: _("{user} reopened this {time_ago}"),
    Comment.PINNED: _("{user} pinned this {time_ago}"),
    Comment.UNPINNED: _("{user} unpinned this {time_ago}"),
}


@register.simple_tag()
def get_comment_action_text(comment):
    user_frag = '<a href="{url}">{user}</a>'
    date_frag = '<span title="{title}">{date}</span>'
    text_frag = ACTIONS.get(comment.action, "{user} unknown action {time_ago}")
    if comment.is_removed:
        text_frag = _("{user}'s comment was removed {time_ago}")
    return format_html(
        text_frag,
        user=format_html(
            user_frag,
            url=comment.user.st.get_absolute_url(),
            user=comment.user.st.nickname),
        time_ago=format_html(
            date_frag,
            title=date_format(comment.date, "DATETIME_FORMAT"),
            date=humanize.naturaltime(comment.date)))


@register.simple_tag(takes_context=True)
def post_render_comment(context, comment):
    request = context['request']
    csrf_token = context['csrf_token']
    return mark_safe(render_polls(comment, request, csrf_token))
