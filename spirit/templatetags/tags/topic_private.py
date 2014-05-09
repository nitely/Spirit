#-*- coding: utf-8 -*-

from . import register
from spirit.forms.topic_private import TopicPrivateInviteForm


@register.inclusion_tag('spirit/topic_private/_private_invite_form.html')
def render_invite_form(topic, next=None):
    form = TopicPrivateInviteForm()
    return {'form': form, 'topic': topic, 'next': next}