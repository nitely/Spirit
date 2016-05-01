# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib

from django.conf import settings
from django.core.cache import caches


TIME_DICT = {
    's': 1,
    'm': 60,
}


class RateLimitError(Exception):
    """"""


class RateLimit:

    def __init__(self, request, uid, method=None, field=None, rate='5/5m'):
        self.request = request
        self.uid = uid
        self.method = method or ['POST', ]
        self.limit = None
        self.time = None
        self.cache_keys = []
        self.cache_values = []

        if self.request.method in (m.upper() for m in self.method)\
                and settings.ST_RATELIMIT_ENABLE:
            self.limit, self.time = self.split_rate(rate)
            self.cache_keys = self._get_keys(field)
            self.cache_values = self._incr_all()

    def split_rate(self, rate):
        limit, period = rate.split('/')
        limit = int(limit)

        if len(period) > 1:
            time = TIME_DICT[period[-1]]
            time *= int(period[:-1])
        else:
            time = TIME_DICT[period]

        return limit, time

    def _make_key(self, key):
        key_uid = '%s:%s' % (self.uid, key)
        key_hash = hashlib.sha1(key_uid.encode('utf-8')).hexdigest()
        return '%s:%s' % (settings.ST_RATELIMIT_CACHE_PREFIX, key_hash)

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
