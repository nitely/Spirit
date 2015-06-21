# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from spirit.templatetags.registry import register
from .forms import TopicPollVoteManyForm


@register.inclusion_tag('spirit/topic/poll/_form.html')
def render_poll_form(topic, user, next=None):
    try:
        poll = topic.poll
    except models.ObjectDoesNotExist:
        return {}

    form = TopicPollVoteManyForm(user=user, poll=poll)

    if user.is_authenticated():
        form.load_initial()

    return {'form': form, 'poll': poll, 'next': next}
