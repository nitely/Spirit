#-*- coding: utf-8 -*-

from django.db import models

from . import register
from spirit.forms.topic_poll import TopicPollVoteManyForm


@register.simple_tag()
def render_poll(topic, user):
    try:
        poll = topic.poll
    except models.ObjectDoesNotExist:
        return ""

    form = TopicPollVoteManyForm(user=user, poll=poll)
    form.load_initial()
    #votes = choices.objects.filter(voters=user)

    return form.as_p()