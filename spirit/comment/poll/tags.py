# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re

from django.template.loader import render_to_string

from ...core.tags.registry import register
from .forms import PollVoteManyForm


def _render_form(poll, comment, request):
    form = PollVoteManyForm(poll=poll)

    if request.user.is_authenticated():
        form.load_initial()

    context = {
        'form': form,
        'poll': poll,
        'comment': comment,
        'user': request.user,
        'request': request
    }

    return render_to_string('spirit/comment/poll/_form.html', context)


def _render_results(poll, comment, request):
    context = {
        'poll': poll,
        'comment': comment,
        'user': request.user,
        'request': request
    }

    return render_to_string('spirit/comment/poll/_results.html', context)


def _evaluate(polls_by_name, comment, request):
    def evaluate(m):
        name = m.group('name')
        poll = polls_by_name[name]

        if poll.pk == request.GET.get('show_poll'):
            return _render_results(poll, comment, request)
        else:
            return _render_form(poll, comment, request)

    return evaluate


def render_polls(comment, request):
    # todo: return safe string
    polls_by_name = {poll.name: poll for poll in comment.polls}

    if not polls_by_name:
        return comment.comment_html

    evaluate = _evaluate(polls_by_name, comment, request)
    return re.sub(r'(?:<poll\s+name=(?P<name>[\w\-_]+)>)', evaluate, comment.comment_html)


@register.simple_tag(takes_context=True)
def render_comment(context, comment):
    # todo: move to comment.tags
    request = context['request']
    return render_polls(comment, request)
