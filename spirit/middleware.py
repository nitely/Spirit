# -*- coding: utf-8 -*-

from spirit.apps.core.middleware import XForwardedForMiddleware, PrivateForumMiddleware
from spirit.apps.user.middleware import TimezoneMiddleware, LastIPMiddleware,\
    LastSeenMiddleware, ActiveUserMiddleware

# TODO: remove in Spirit 0.4


__all__ = [
    'XForwardedForMiddleware',
    'PrivateForumMiddleware',
    'TimezoneMiddleware',
    'LastIPMiddleware',
    'LastSeenMiddleware',
    'ActiveUserMiddleware'
]