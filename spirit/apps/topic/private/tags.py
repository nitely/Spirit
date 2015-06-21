# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from spirit.templatetags.registry import register
from .forms import TopicPrivateInviteForm


@register.inclusion_tag('spirit/topic/private/_invite_form.html')
def render_invite_form(topic, next=None):
    form = TopicPrivateInviteForm()
    return {'form': form, 'topic': topic, 'next': next}
