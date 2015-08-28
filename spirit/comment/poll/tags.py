# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re

from django.template.loader import render_to_string

from ...core.tags.registry import register
from .forms import PollVoteManyForm


def _render_form(poll, user, comment):
    form = PollVoteManyForm(poll=poll)
    # form.load_initial(votes)
    context = {
        'form': form,
        'poll': poll,
        'user': user,
        'comment': comment
    }
    return render_to_string('spirit/comment/poll/_form.html', context)


def _evaluate(polls_by_name, user, comment):
    def evaluate(m):
        name = m.group('name')
        poll = polls_by_name[name]

        if user.is_authenticated():
            return _render_form(poll, user, comment)  # todo: render form or results
        else:
            return poll.name

    return evaluate


@register.simple_tag()
def render_polls(comment, user):
    # todo: return safe string
    polls_by_name = {poll.name: poll for poll in comment.polls}

    if not polls_by_name:
        return comment.comment_html

    evaluate = _evaluate(polls_by_name, user, comment)
    return re.sub(r'(?:<poll\s+name=(?P<name>[\w\-_]+)>)', evaluate, comment.comment_html)
