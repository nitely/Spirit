# -*- coding: utf-8 -*-

from spirit.core.middleware import XForwardedForMiddleware, PrivateForumMiddleware
from spirit.user.middleware import TimezoneMiddleware, LastIPMiddleware,\
    LastSeenMiddleware, ActiveUserMiddleware

# TODO: remove in Spirit 0.5


__all__ = [
    'XForwardedForMiddleware',
    'PrivateForumMiddleware',
    'TimezoneMiddleware',
    'LastIPMiddleware',
    'LastSeenMiddleware',
    'ActiveUserMiddleware'
]