# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib
import time

from django.conf import settings
from django.core.cache import caches


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

    # Some third-party backend
    # don't have a TIMEOUT option
    if (not settings.ST_RATELIMIT_IGNORE_TIMEOUT_WARNING and
            cache.get('TIMEOUT', 1) is not None):
        # todo: raise ConfigurationError in next version
        # todo: warn(
        #   'settings.ST_RATELIMIT_CACHE cache's TIMEOUT '
        #   'must be None (never expire) and it should '
        #   'be other than the default. See spirit.settings. '
        #   'To ignore this warning, set '
        #   'settings.ST_RATELIMIT_IGNORE_TIMEOUT to True, '
        #   'if you know what you are doing.')
        pass


class RateLimitError(Exception):
    """"""


class RateLimit:

    def __init__(self, request, uid, method=None, field=None, rate='5/5m'):
        validate_cache_config()
        self.request = request
        self.uid = uid
        self.method = method or ['POST']
        self.limit = None
        self.time = None
        self.cache_keys = []
        self.cache_values = []

        if (self.request.method in (m.upper() for m in self.method) and
                settings.ST_RATELIMIT_ENABLE):
            self.limit, self.time = self.split_rate(rate)
            self.cache_keys = self._get_keys(field)
            self.cache_values = self._incr_all()

    @staticmethod
    def split_rate(rate):
        limit, period = rate.split('/')
        limit = int(limit)

        if len(period) > 1:
            time_ = TIME_DICT[period[-1]]
            time_ *= int(period[:-1])
        else:
            time_ = TIME_DICT[period]

        return limit, time_

    @staticmethod
    def get_fixed_window(period):
        if not period:  # todo: assert on Spirit 0.5
            return 0

        timestamp = int(time.time())
        return timestamp - timestamp % period

    @staticmethod
    def _make_hash(key):
        return hashlib.sha1(key.encode('utf-8')).hexdigest()

    def _make_key(self, key):
        key_uid = '%s:%s:%d' % (
            self.uid, key, self.get_fixed_window(self.time))
        return '%s:%s' % (
            settings.ST_RATELIMIT_CACHE_PREFIX,
            self._make_hash(key_uid))

    def _get_keys(self, field=None):
        keys = []

        if self.request.user.is_authenticated():
            keys.append('user:%d' % self.request.user.pk)
        else:
            keys.append('ip:%s' % self.request.META['REMOTE_ADDR'])

        if field is not None:
            field_value = getattr(self.request, self.request.method).get(field, '')

            if field_value:
                keys.append('field:%s:%s' % (field, field_value))

        return [self._make_key(k) for k in keys]

    def __incr(self, key):
        cache = caches[settings.ST_RATELIMIT_CACHE]
        cache.add(key, 0, timeout=self.time)

        try:
            # This resets the timeout to
            # default, see Django ticket #26619
            return cache.incr(key)
        except ValueError:  # Key does not exists
            raise RateLimitError

    def _incr(self, key):
        try:
            return self.__incr(key)
        except RateLimitError:
            pass

        try:
            # Retry in case the key
            # has just timed-out
            return self.__incr(key)
        except RateLimitError:
            # The timeout is too low
            # or the cache is being pruned
            # too frequently
            return 1

    def _incr_all(self):
        return [self._incr(k) for k in self.cache_keys]

    def is_limited(self):
        return any(
            count > self.limit
            for count in self.cache_values)
