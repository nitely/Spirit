# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ..conf import settings as st_settings

from .registry import register


@register.simple_tag(takes_context=True)
def load_settings(context, *settings):
    context['st_settings'] = {
        setting: getattr(st_settings, setting)
        for setting in settings}
    return ''
