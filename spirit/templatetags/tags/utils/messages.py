# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from collections import OrderedDict

from django.contrib.messages import constants

from .. import register


TAGS = {
    constants.DEBUG: 'debug',
    constants.INFO: 'info',
    constants.SUCCESS: 'success',
    constants.WARNING: 'warning',
    constants.ERROR: 'error',
}


@register.inclusion_tag('spirit/utils/_messages.html')
def render_messages(messages):
    grouped = OrderedDict()

    for m in messages:
        messages_group = grouped.get(TAGS[m.level], [])
        messages_group.append(m)
        grouped[TAGS[m.level]] = messages_group

    return {'messages_grouped': grouped, }
