# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import re

from ...core.tags.registry import register


def _evaluate(polls_by_name):
    def evaluate(m):
        name = m.group('name')
        poll = polls_by_name[name]
        return poll.name  # todo: render form or results

    return evaluate


@register.simple_tag()
def parse_polls(comment, next=None):
    # todo: return safe string
    polls_by_name = {poll.name: poll for poll in comment.polls}

    if not polls_by_name:
        return comment.comment_html

    evaluate = _evaluate(polls_by_name)
    return re.sub(r'(?:<poll\s+name=(?P<name>[\w\-_]+)>)', evaluate, comment.comment_html)
