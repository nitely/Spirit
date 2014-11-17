# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

from . import register
from spirit.forms.topic_poll import TopicPollVoteManyForm


@register.inclusion_tag('spirit/topic_poll/_form.html')
def render_poll_form(topic, user, next=None):
    try:
        poll = topic.poll
    except models.ObjectDoesNotExist:
        return {}

    form = TopicPollVoteManyForm(user=user, poll=poll)

    if user.is_authenticated():
        form.load_initial()

    return {'form': form, 'poll': poll, 'next': next}
