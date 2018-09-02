# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re

from django.template.loader import render_to_string

from ..forms import PollVoteManyForm


__all__ = ['PATTERN', 'render_polls']


PATTERN = re.compile(r'(?:<poll\s+name=(?P<name>[\w\-_]+)>)')


def _render_form(poll, comment, request, csrf_token):
    form = PollVoteManyForm(poll=poll)

    if request.user.is_authenticated:
        form.load_initial()

    context = {
        'form': form,
        'poll': poll,
        'comment': comment,
        'show_poll': poll.pk if not poll.has_user_voted else 0,
        'user': request.user,
        'request': request,
        'csrf_token': csrf_token,
        'next': poll.get_rel_url(request)  # todo: add ?hash_tag=pX to comment.find and use the poll.url
    }

    return render_to_string('spirit/comment/poll/_form.html', context)


def _render_results(poll, comment, request, csrf_token):
    context = {
        'poll': poll,
        'comment': comment,
        'show_poll': poll.pk if poll.has_user_voted else 0,
        'user': request.user,
        'request': request,
        'csrf_token': csrf_token
    }

    return render_to_string('spirit/comment/poll/_results.html', context)


def _evaluate(polls_by_name, comment, request, csrf_token):
    def evaluate(m):
        name = m.group('name')
        poll = polls_by_name[name]
        show_poll = str(poll.pk) == request.GET.get('show_poll')  # Results or choices
        show_results = (
            (not poll.has_user_voted and show_poll) or
            (poll.has_user_voted and not show_poll)
        )

        if poll.is_closed or (poll.can_show_results and show_results):
            return _render_results(poll, comment, request, csrf_token)
        else:
            return _render_form(poll, comment, request, csrf_token)

    return evaluate


def render_polls(comment, request, csrf_token):
    if not comment.polls:
        return comment.comment_html

    evaluate = _evaluate(
        polls_by_name={poll.name: poll for poll in comment.polls},
        comment=comment,
        request=request,
        csrf_token=csrf_token
    )
    return re.sub(PATTERN, evaluate, comment.comment_html)
