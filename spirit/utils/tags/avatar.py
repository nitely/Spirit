# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import math

from django.utils.encoding import smart_text

from spirit.templatetags.registry import register


@register.simple_tag()
def get_avatar_color(user):
    # returns 0-215
    return smart_text(int(215 * math.log10(user.pk)))
