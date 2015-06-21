# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import functools

from django.contrib import messages
from django.utils.translation import ugettext as _

from spirit.utils.ratelimit.ratelimit import RateLimit


__all__ = ['ratelimit', ]


def ratelimit(method=None, field=None, rate='5/5m'):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            uid = '.'.join((func.__module__, func.__name__))
            rl = RateLimit(request, uid, method=method, field=field, rate=rate)
            request.is_limited = rl.is_limited()

            if request.is_limited:
                messages.error(request, _("Too many submissions, wait %(time)s.") % {'time': rate.split('/')[1], })

            return func(request, *args, **kwargs)

        return wrapper

    return decorator
