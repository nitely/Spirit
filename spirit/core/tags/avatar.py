# -*- coding: utf-8 -*-

from .registry import register


@register.simple_tag()
def get_avatar_color(user_id):
    hue = (user_id % 37) * 10
    return 'hsl({}, 75%, 25%)'.format(hue)
