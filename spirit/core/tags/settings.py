# -*- coding: utf-8 -*-

from spirit.core.conf import settings as st_settings

from .registry import register


@register.simple_tag(takes_context=True)
def load_settings(context, *settings):
    context.setdefault('st_settings', {}).update({
        setting: getattr(st_settings, setting)
        for setting in settings})
    return ''
