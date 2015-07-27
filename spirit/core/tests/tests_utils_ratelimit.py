# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import hashlib

from django.core.cache import cache
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.conf import settings
from django.core.cache import caches

from ..utils.ratelimit import RateLimit
from ..utils.ratelimit.decorators import ratelimit


def setup_request_factory_messages(req):
    # RequestFactory: It does not support middleware.
    # Session and authentication attributes must be supplied
    # by the test itself if required for the view to function properly.
    setattr(req, 'session', 'session')
    messages = FallbackStorage(req)
    setattr(req, '_messages', messages)


class UtilsRateLimitTests(TestCase):

    def setUp(self):
        cache.clear()

    def test_rate_limit_split_rate(self):
        req = RequestFactory().post('/')
        req.user = AnonymousUser()
        rl = RateLimit(req, 'func_name')
        self.assertEqual(rl.split_rate('5/m'), (5, 60))
        self.assertEqual(rl.split_rate('5/5m'), (5, 60 * 5))
        self.assertEqual(rl.split_rate('5/s'), (5, 1))
        self.assertEqual(rl.split_rate('5/5s'), (5, 1 * 5))
        self.assertEqual(rl.split_rate('5/15s'), (5, 15))
        self.assertEqual(rl.split_rate('15/15s'), (15, 15))

    def test_rate_limit_user_or_ip(self):
        req = RequestFactory().get('/')
        req.user = AnonymousUser()
        setup_request_factory_messages(req)

        @ratelimit(method=['GET', ], rate='1/m')
        def limit_ip(request):
            return request.is_limited

        self.assertFalse(limit_ip(req))
        self.assertTrue(limit_ip(req))

        req.user = User()
        req.user.pk = 1

        self.assertFalse(limit_ip(req))
        self.assertTrue(limit_ip(req))

    def test_rate_limit_method(self):
        rf = RequestFactory()
        post = rf.post('/')
        get = rf.get('/')
        post.user = AnonymousUser()
        get.user = AnonymousUser()
        setup_request_factory_messages(get)
        setup_request_factory_messages(post)

        @ratelimit(method=['POST', ], rate='1/m')
        def limit_post(request):
            return request.is_limited

        self.assertFalse(limit_post(post))
        self.assertTrue(limit_post(post))
        self.assertFalse(limit_post(get))

    def test_rate_limit_field(self):
        req = RequestFactory().post('/', {'username': 'esteban', })
        req.user = AnonymousUser()
        setup_request_factory_messages(req)

        @ratelimit(field='username', rate='1/m')
        def username(request):
            return request.is_limited

        self.assertFalse(username(req))
        self.assertTrue(username(req))

        req.user = User()
        req.user.pk = 1

        self.assertTrue(username(req))

    def test_rate_limit_field_empty(self):
        empty = RequestFactory().post('/', {'username': '', })
        empty.user = AnonymousUser()

        @ratelimit(field='username', rate='1/m')
        def username(request):
            return request.is_limited

        self.assertFalse(username(empty))

        empty.user = User()
        empty.user.pk = 1

        self.assertFalse(username(empty))

    def test_rate_limit_rate(self):
        req = RequestFactory().post('/')
        req.user = AnonymousUser()
        setup_request_factory_messages(req)

        @ratelimit(rate='2/m')
        def two(request):
            return request.is_limited

        self.assertFalse(two(req))
        self.assertFalse(two(req))
        self.assertTrue(two(req))

    def test_rate_limit_hash_key(self):
        """
        Keys should be stored as hashes
        """
        req = RequestFactory().post('/')
        req.user = User()
        req.user.pk = 1
        RateLimit(req, 'func_name')
        rl_cache = caches[settings.ST_RATELIMIT_CACHE]
        self.assertIsNotNone(rl_cache.get('srl:02b3cee0bd2a40ec0fca9b1bef06fb560a081673'))

    def test_rate_limit_unique_key(self):
        """
        Keys should contain the full module path and function name
        """
        req = RequestFactory().post('/')
        req.user = User()
        req.user.pk = 1

        @ratelimit(rate='1/m')
        def one(request):
            pass

        key_part = '%s.%s:user:%d' % (one.__module__, one.__name__, req.user.pk)
        key_hash = hashlib.sha1(key_part.encode('utf-8')).hexdigest()
        key = '%s:%s' % (settings.ST_RATELIMIT_CACHE_PREFIX, key_hash)

        one(req)
        rl_cache = caches[settings.ST_RATELIMIT_CACHE]
        self.assertIsNotNone(rl_cache.get(key))