# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib
import time

from django.core.cache import caches

from ...conf import settings
from ..deprecations import warn


__all__ = ['RateLimit']


TIME_DICT = {
    's': 1,
    'm': 60}


def validate_cache_config():
    try:
        cache = settings.CACHES[settings.ST_RATELIMIT_CACHE]
    except KeyError:
        # Django will raise later when using
        # this cache so we do nothing
        return

    if (not settings.ST_RATELIMIT_SKIP_TIMEOUT_CHECK and
            cache.get('TIMEOUT', 1) is not None):
        # todo: ConfigurationError in next version
        warn(
           'settings.ST_RATELIMIT_CACHE cache\'s TIMEOUT '
           'must be None (never expire) and it may '
           'be other than the default cache. '
           'To skip this check, for example when using '
           'a third-party backend with no TIMEOUT option, set '
           'settings.ST_RATELIMIT_SKIP_TIMEOUT_CHECK to True. '
           'This will raise an exception in next version.')


def split_rate(rate):
    limit, period = rate.split('/')
    limit = int(limit)

    if len(period) > 1:
        time_ = TIME_DICT[period[-1]]
        time_ *= int(period[:-1])
    else:
        time_ = TIME_DICT[period]

    return limit, time_


def fixed_window(period):
    if settings.ST_TESTS_RATELIMIT_NEVER_EXPIRE:
        return 0

    if not period:  # todo: assert on Spirit 0.5
        warn('Period must be greater than 0.')
        return time.time()  # Closer to no period

    timestamp = int(time.time())
    return timestamp - timestamp % period


def make_hash(key):
    return (hashlib
            .sha1(key.encode('utf-8'))
            .hexdigest())


class RateLimit:

    def __init__(self, request, uid, methods=None, field=None, rate='5/5m'):
        validate_cache_config()
        self.request = request
        self.uid = uid
        self.methods = methods or ['POST']
        self.rate = rate
        self.limit = None
        self.time = None
        self.cache_keys = []

        if self.request.method in self.methods:
            self.limit, self.time = split_rate(rate)
            self.cache_keys = self._get_keys(field)

    def _make_key(self, key):
        key_uid = '%s:%s:%d' % (
            self.uid, key, fixed_window(self.time))
        return '%s:%s' % (
            settings.ST_RATELIMIT_CACHE_PREFIX,
            make_hash(key_uid))

    def _get_keys(self, field=None):
        keys = []

        if self.request.user.is_authenticated:
            keys.append('user:%d' % self.request.user.pk)
        else:
            keys.append('ip:%s' % self.request.META['REMOTE_ADDR'])

        if field is not None:
            field_value = (getattr(self.request, self.request.method)
                           .get(field, ''))

            if field_value:
                keys.append('field:%s:%s' % (field, field_value))

        return [self._make_key(k) for k in keys]

    def _get_cache_values(self):
        return (caches[settings.ST_RATELIMIT_CACHE]
                .get_many(self.cache_keys))

    def _incr(self, key):
        cache = caches[settings.ST_RATELIMIT_CACHE]
        cache.add(key, 0)

        try:
            # This resets the timeout to
            # default, see Django ticket #26619
            return cache.incr(key)
        except ValueError:  # Key does not exists
            # The cache is being
            # pruned too frequently
            return 1

    def incr(self):
        return [self._incr(k) for k in self.cache_keys]

    def is_limited(self, increment=True):
        if not settings.ST_RATELIMIT_ENABLE:
            return False

        if increment:
            cache_values = self.incr()
        else:
            cache_values = self._get_cache_values()

        return any(
            count > self.limit
            for count in cache_values)
