# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re

from django.template.loader import render_to_string

from ..models import CommentPoll
from .render import PATTERN


def _evaluate(polls_by_name):
    def evaluate(m):
        name = m.group('name')

        context = {
            'poll': polls_by_name[name]
        }

        return render_to_string('spirit/comment/poll/_static.html', context)

    return evaluate


def _render_polls(comment):
    polls = CommentPoll.objects\
        .for_comment(comment)\
        .unremoved()\
        .with_choices()

    if not polls:
        return comment.comment_html

    evaluate = _evaluate(polls_by_name={poll.name: poll for poll in polls})
    return re.sub(PATTERN, evaluate, comment.comment_html)


def post_render_static_polls(comment):
    # This is used by the comment history
    return _render_polls(comment)
