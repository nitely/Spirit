# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import hashlib

from django.conf import settings
from django.core.cache import get_cache


TIME_DICT = {
    's': 1,
    'm': 60,
}


class RateLimit:

    def __init__(self, request, uid, method=None, field=None, rate='5/5m'):
        self.request = request
        self.uid = uid
        self.method = method or ['POST', ]
        self.limit = None
        self.time = None
        self.cache_keys = []
        self.cache_values = {}

        if self.request.method in [m.upper() for m in self.method]\
                and settings.ST_RATELIMIT_ENABLE:
            self.limit, self.time = self.split_rate(rate)
            self.cache_keys = self._get_keys(field)
            self.cache_values = self._incr_cache()

    def split_rate(self, rate):
        limit, period = rate.split('/')
        limit = int(limit)

        if len(period) > 1:
            time = TIME_DICT[period[-1]]
            time *= int(period[:-1])
        else:
            time = TIME_DICT[period]

        return limit, time

    def _make_cache_key(self, key):
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

        return [self._make_cache_key(k) for k in keys]

    def _incr_cache(self):
        if not self.cache_keys:
            return {}

        cache = get_cache(settings.ST_RATELIMIT_CACHE)
        cache_values = cache.get_many(self.cache_keys)

        for key in self.cache_keys:
            if key in cache_values:
                cache_values[key] += 1
            else:
                cache_values[key] = 1

        cache.set_many(cache_values, timeout=self.time)
        return cache_values

    def is_limited(self):
        for count in self.cache_values.values():
            if count > self.limit:
                return True

        return False
