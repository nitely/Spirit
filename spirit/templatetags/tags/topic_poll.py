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

    choices = poll.choices.all()
    #votes = choices.objects.filter(voters=user)

    return ",".join([c.description for c in choices])