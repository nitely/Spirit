# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import warnings

from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.cache import caches

from . import utils
from ..utils.ratelimit import ratelimit as rl_module
from ..utils.ratelimit import RateLimit
from ..utils.ratelimit.decorators import ratelimit
from ..conf import settings


def setup_request_factory_messages(req):
    # RequestFactory: It does not support middleware.
    # Session and authentication attributes must be supplied
    # by the test itself if required for the view to function properly.
    setattr(req, 'session', 'session')
    messages = FallbackStorage(req)
    setattr(req, '_messages', messages)


class UtilsRateLimitTests(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_rate_limit_split_rate(self):
        req = RequestFactory().post('/')
        req.user = AnonymousUser()
        rl = RateLimit(req, 'func_name')
        self.assertEqual(rl_module.split_rate('5/m'), (5, 60))
        self.assertEqual(rl_module.split_rate('5/5m'), (5, 60 * 5))
        self.assertEqual(rl_module.split_rate('5/s'), (5, 1))
        self.assertEqual(rl_module.split_rate('5/5s'), (5, 1 * 5))
        self.assertEqual(rl_module.split_rate('5/15s'), (5, 15))
        self.assertEqual(rl_module.split_rate('15/15s'), (15, 15))

    def test_rate_limit_user_or_ip(self):
        req = RequestFactory().get('/')
        req.user = AnonymousUser()
        setup_request_factory_messages(req)

        @ratelimit(methods=['GET', ], rate='1/m')
        def limit_ip(request):
            return request.is_limited()

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

        @ratelimit(methods=['POST', ], rate='1/m')
        def limit_post(request):
            return request.is_limited()

        self.assertFalse(limit_post(post))
        self.assertTrue(limit_post(post))
        self.assertFalse(limit_post(get))

    def test_rate_limit_field(self):
        req = RequestFactory().post('/', {'username': 'esteban', })
        req.user = AnonymousUser()
        setup_request_factory_messages(req)

        @ratelimit(field='username', rate='1/m')
        def username(request):
            return request.is_limited()

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
            return request.is_limited()

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
            return request.is_limited()

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
        rl = RateLimit(req, 'func_name')
        rl.incr()
        self.assertEqual(
            len(rl.cache_keys[0]),
            len(settings.ST_RATELIMIT_CACHE_PREFIX) + 1 + 40)  # prefix:sha1_hash
        rl_cache = caches[settings.ST_RATELIMIT_CACHE]
        self.assertIsNotNone(rl_cache.get(rl.cache_keys[0]))

    def test_rate_limit_unique_key(self):
        """
        Keys should contain the full\
        module path and function name
        """
        req = RequestFactory().post('/')
        req.user = User()
        req.user.pk = 1

        @ratelimit(rate='1/m')
        def one(request):
            return request.is_limited()

        fixed_now = rl_module.time.time()

        def fixed_time():
            # Cache backend may use time.time(),
            # so better fix to now
            return fixed_now

        org_time_time, rl_module.time.time = rl_module.time.time, fixed_time
        try:
            key_part = '%s.%s:user:%d:%d' % (
                one.__module__,
                one.__name__,
                req.user.pk,
                rl_module.fixed_window(period=60))
            key_hash = rl_module.make_hash(key_part)
            key = '%s:%s' % (settings.ST_RATELIMIT_CACHE_PREFIX, key_hash)

            one(req)
            rl_cache = caches[settings.ST_RATELIMIT_CACHE]
            self.assertIsNotNone(rl_cache.get(key))
        finally:
            rl_module.time.time = org_time_time

    def test_rate_limit_get_fixed_window(self):
        """
        Should return the expiration time
        """
        def fixed_time():
            # Fixed to 50 seconds
            return 1463507750.1

        def fixed_time_future(seconds):
            return fixed_time() + seconds

        org_time_time, rl_module.time.time = rl_module.time.time, fixed_time
        try:
            period = 10
            window = rl_module.fixed_window(period=period)

            # Same window 1 second later
            rl_module.time.time = lambda: fixed_time_future(seconds=1)
            self.assertEqual(window, rl_module.fixed_window(period=period))

            # Same window (period - 1) seconds later
            rl_module.time.time = lambda: fixed_time_future(seconds=period - 1)
            self.assertEqual(window, rl_module.fixed_window(period=period))

            # Next window on period seconds later
            rl_module.time.time = lambda: fixed_time_future(seconds=period)
            self.assertNotEqual(window, rl_module.fixed_window(period=period))
            self.assertEqual(period, rl_module.fixed_window(period=period) - window)
        finally:
            rl_module.time.time = org_time_time

    def test_rate_limit_pruned_too_frequently(self):
        """
        Should not limit when the cache\
        is pruned too frequently
        """
        req = RequestFactory().post('/')
        setup_request_factory_messages(req)
        req.user = User()
        req.user.pk = 1

        @ratelimit(rate='1/m')
        def one(request):
            return request.is_limited()

        foo_cache = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
            },
            'foo': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'foo',
                'TIMEOUT': 0  # Faking cache pruned too frequently
            }}

        with override_settings(CACHES=foo_cache, ST_RATELIMIT_CACHE='foo'):
            with warnings.catch_warnings(record=True):  # Ignore warnings
                caches['foo'].clear()
                self.assertFalse(one(req))
                self.assertFalse(one(req))


class UtilsRateLimitDeprecationsTests(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_validator_conf(self):
        """
        Should create a deprecation\
        warning when cache has no timeout
        """
        req = RequestFactory().post('/')
        req.user = User()
        req.user.pk = 1

        @ratelimit(rate='1/m')
        def one(_):
            pass

        foo_cache = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
            },
            'foo': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'foo'}}

        with override_settings(CACHES=foo_cache, ST_RATELIMIT_CACHE='foo'):
            with warnings.catch_warnings(record=True) as w:
                utils.cache_clear()
                one(req)
                self.assertEqual(len(w), 1)
                self.assertEqual(
                    str(w[-1].message),
                    'settings.ST_RATELIMIT_CACHE cache\'s TIMEOUT '
                    'must be None (never expire) and it may '
                    'be other than the default cache. '
                    'To skip this check, for example when using '
                    'a third-party backend with no TIMEOUT option, set '
                    'settings.ST_RATELIMIT_SKIP_TIMEOUT_CHECK to True. '
                    'This will raise an exception in next version.')

        foo_cache['foo']['TIMEOUT'] = None

        with override_settings(CACHES=foo_cache, ST_RATELIMIT_CACHE='foo'):
            with warnings.catch_warnings(record=True) as w:
                caches['foo'].clear()
                one(req)
                self.assertEqual(len(w), 0)

    def test_get_fixed_window(self):
        """
        Should create a deprecation\
        warning when period is zero
        """
        with warnings.catch_warnings(record=True) as w:
            rl_module.fixed_window(period=0)
            self.assertEqual(len(w), 1)
            self.assertEqual(
                str(w[-1].message),
                'Period must be greater than 0.')
