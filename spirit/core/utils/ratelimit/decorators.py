# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import functools

from django.contrib import messages
from django.utils.translation import ugettext as _

from .ratelimit import RateLimit


__all__ = ['ratelimit']


def _is_limited(request, rate, rl):
    """
    Wrapper to show an error\
    message when request is limited
    """
    def inner(*args, **kwargs):
        is_limited = rl.is_limited(*args, **kwargs)

        if is_limited:
            messages.error(
                request,
                _("Too many submissions, wait %(time)s.") % {
                    'time': rate.split('/')[1]})

        return is_limited

    return inner


def ratelimit(methods=None, field=None, rate='5/5m'):
    methods = set(m.upper() for m in methods or [])

    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            uid = '.'.join((func.__module__, func.__name__))
            rl = RateLimit(request, uid, methods=methods, field=field, rate=rate)
            request.is_limited = _is_limited(request=request, rate=rate, rl=rl)
            return func(request, *args, **kwargs)

        return wrapper

    return decorator
