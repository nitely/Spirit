# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.shortcuts import resolve_url
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.conf import settings

from .. import middleware
from . import utils as test_utils


class XForwardedForMiddlewareTests(TestCase):

    def test_meta(self):
        """
        Should add remote addr to request meta data
        """
        req = RequestFactory().get('/')
        req.META['REMOTE_ADDR'] = ''
        self.assertEqual(req.META['REMOTE_ADDR'], '')
        http_x_fwd_for = 'evil.ip, foo.ip, org.ip'
        req.META['HTTP_X_FORWARDED_FOR'] = http_x_fwd_for
        self.assertEqual(req.META['HTTP_X_FORWARDED_FOR'], http_x_fwd_for)
        middleware.XForwardedForMiddleware().process_request(req)
        self.assertEqual(req.META['HTTP_X_FORWARDED_FOR'], http_x_fwd_for)
        self.assertEqual(req.META['REMOTE_ADDR'], 'org.ip')

    def test_meta_weird_format(self):
        """
        Should add remote addr to request meta data
        """
        req = RequestFactory().get('/')
        req.META['REMOTE_ADDR'] = ''
        self.assertEqual(req.META['REMOTE_ADDR'], '')
        http_x_fwd_for = 'evil.ip, foo.ip,,bar.ip, baz.ip,  org.ip  '
        req.META['HTTP_X_FORWARDED_FOR'] = http_x_fwd_for
        self.assertEqual(req.META['HTTP_X_FORWARDED_FOR'], http_x_fwd_for)
        middleware.XForwardedForMiddleware().process_request(req)
        self.assertEqual(req.META['HTTP_X_FORWARDED_FOR'], http_x_fwd_for)
        self.assertEqual(req.META['REMOTE_ADDR'], 'org.ip')


class PrivateForumMiddlewareTests(TestCase):

    def setUp(self):
        test_utils.cache_clear()
        self.user = test_utils.create_user()

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_anonym_user(self):
        """
        Should restrict the URL
        """
        req = RequestFactory().get(resolve_url('spirit:index'))
        req.user = AnonymousUser()
        resp = middleware.PrivateForumMiddleware().process_request(req)
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(
            resp['Location'],
            resolve_url(settings.LOGIN_URL) + '?next=/')

    @override_settings(ST_PRIVATE_FORUM=False)
    def test_anonym_user_non_private(self):
        """
        Should not restrict the URL
        """
        req = RequestFactory().get(resolve_url('spirit:index'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware().process_request(req))

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_authenticated_user(self):
        """
        Should not restrict authenticated users
        """
        req = RequestFactory().get(resolve_url('spirit:index'))
        req.user = self.user
        self.assertTrue(self.user.is_authenticated())
        self.assertIsNone(
            middleware.PrivateForumMiddleware().process_request(req))

    @override_settings(ST_PRIVATE_FORUM=False)
    def test_authenticated_user_not_private(self):
        """
        Should not restrict authenticated users
        """
        req = RequestFactory().get(resolve_url('spirit:index'))
        req.user = self.user
        self.assertTrue(self.user.is_authenticated())
        self.assertIsNone(
            middleware.PrivateForumMiddleware().process_request(req))

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_auth_paths(self):
        """
        Should not restrict auth paths
        """
        req = RequestFactory().get(resolve_url('spirit:index'))
        req.user = AnonymousUser()
        self.assertIsInstance(
            middleware.PrivateForumMiddleware().process_request(req),
            HttpResponseRedirect)
        req = RequestFactory().get(resolve_url('spirit:user:auth:login'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware().process_request(req))
        req = RequestFactory().get(resolve_url('spirit:user:auth:register'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware().process_request(req))
        req = RequestFactory().get(resolve_url('spirit:user:auth:logout'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware().process_request(req))
        req = RequestFactory().get(resolve_url('spirit:user:auth:resend-activation'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware().process_request(req))

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_not_spirit(self):
        """
        Should not restrict other apps URLs
        """
        req = RequestFactory().get(resolve_url('spirit:index'))
        req.user = AnonymousUser()
        self.assertIsInstance(
            middleware.PrivateForumMiddleware().process_request(req),
            HttpResponseRedirect)
        req = RequestFactory().get(resolve_url('admin:index'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware().process_request(req))
        req = RequestFactory().get(resolve_url('admin:index'))
        req.user = self.user
        self.assertIsNone(
            middleware.PrivateForumMiddleware().process_request(req))
