# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings as django_settings

from .registry import register


@register.simple_tag(takes_context=True)
def load_settings(context, *settings):
    context['st_settings'] = {
        setting: getattr(django_settings, setting)
        for setting in settings}
    return ''
