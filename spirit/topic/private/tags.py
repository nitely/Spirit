# -*- coding: utf-8 -*-

from ...core.tags.registry import register
from .forms import TopicPrivateInviteForm


@register.inclusion_tag('spirit/topic/private/_invite_form.html')
def render_invite_form(topic, next=None):
    form = TopicPrivateInviteForm()
    return {'form': form, 'topic': topic, 'next': next}
