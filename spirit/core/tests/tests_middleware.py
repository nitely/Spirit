# -*- coding: utf-8 -*-

from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect, HttpResponse
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
        self.assertIsNone(
            middleware.XForwardedForMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
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
        self.assertIsNone(
            middleware.XForwardedForMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        self.assertEqual(req.META['HTTP_X_FORWARDED_FOR'], http_x_fwd_for)
        self.assertEqual(req.META['REMOTE_ADDR'], 'org.ip')

    MIDDLEWARE_WITH_X_FWD = settings.MIDDLEWARE[:]
    if 'spirit.core.middleware.XForwardedForMiddleware' not in settings.MIDDLEWARE:
        MIDDLEWARE_WITH_X_FWD.append('spirit.core.middleware.XForwardedForMiddleware')

    @override_settings(MIDDLEWARE=MIDDLEWARE_WITH_X_FWD)
    def test_on_client(self):
        """
        Should be called on a request
        """
        class XForwardedForMiddlewareMock(middleware.XForwardedForMiddleware):
            _mock_calls = []
            def process_request(self, request):
                self._mock_calls.append(request)
                return super(XForwardedForMiddlewareMock, self).process_request(request)

        org_mid, middleware.XForwardedForMiddleware = (
            middleware.XForwardedForMiddleware, XForwardedForMiddlewareMock)
        try:
            self.client.get(
                reverse('spirit:index'),
                HTTP_X_FORWARDED_FOR='evil.ip, org.ip')
        finally:
            middleware.XForwardedForMiddleware = org_mid

        self.assertEqual(len(XForwardedForMiddlewareMock._mock_calls), 1)
        self.assertEqual(
            XForwardedForMiddlewareMock._mock_calls[0].META['REMOTE_ADDR'],
            'org.ip')


class PrivateForumMiddlewareTests(TestCase):

    def setUp(self):
        test_utils.cache_clear()
        self.user = test_utils.create_user()

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_anonym_user(self):
        """
        Should restrict the URL
        """
        req = RequestFactory().get(reverse('spirit:index'))
        req.user = AnonymousUser()
        resp = (
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        self.assertIsInstance(resp, HttpResponseRedirect)
        self.assertEqual(
            resp['Location'],
            reverse(settings.LOGIN_URL) + '?next=/')

    @override_settings(ST_PRIVATE_FORUM=False)
    def test_anonym_user_non_private(self):
        """
        Should not restrict the URL
        """
        req = RequestFactory().get(reverse('spirit:index'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_authenticated_user(self):
        """
        Should not restrict authenticated users
        """
        req = RequestFactory().get(reverse('spirit:index'))
        req.user = self.user
        self.assertTrue(self.user.is_authenticated)
        self.assertIsNone(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))

    @override_settings(ST_PRIVATE_FORUM=False)
    def test_authenticated_user_not_private(self):
        """
        Should not restrict authenticated users
        """
        req = RequestFactory().get(reverse('spirit:index'))
        req.user = self.user
        self.assertTrue(self.user.is_authenticated)
        self.assertIsNone(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_auth_paths(self):
        """
        Should not restrict auth paths
        """
        req = RequestFactory().get(reverse('spirit:index'))
        req.user = AnonymousUser()
        self.assertIsInstance(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
                .process_request(req),
            HttpResponseRedirect)
        req = RequestFactory().get(reverse('spirit:user:auth:login'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        req = RequestFactory().get(reverse('spirit:user:auth:register'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        req = RequestFactory().get(reverse('spirit:user:auth:logout'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        req = RequestFactory().get(reverse('spirit:user:auth:resend-activation'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_not_spirit(self):
        """
        Should not restrict other apps URLs
        """
        req = RequestFactory().get(reverse('spirit:index'))
        req.user = AnonymousUser()
        self.assertIsInstance(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
                .process_request(req),
            HttpResponseRedirect)
        req = RequestFactory().get(reverse('admin:index'))
        req.user = AnonymousUser()
        self.assertIsNone(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))
        req = RequestFactory().get(reverse('admin:index'))
        req.user = self.user
        self.assertIsNone(
            middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
            .process_request(req))

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_on_client(self):
        """
        Should be called on a request
        """
        response = self.client.get(reverse('spirit:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(
            reverse(settings.LOGIN_URL) + '?next=/' in response['Location'])
        test_utils.login(self)
        self.assertEqual(
            self.client.get(reverse('spirit:index')).status_code, 200)

    @override_settings(ST_PRIVATE_FORUM=False)
    def test_on_client_not_private(self):
        """
        Should be called on a request
        """
        self.assertEqual(
            self.client.get(reverse('spirit:index')).status_code, 200)

    @override_settings(ST_PRIVATE_FORUM=True)
    def test_restrict_apps(self):
        """
        Should restrict the URLs
        """
        url_names = [
            'spirit:topic:index-active',
            'spirit:topic:private:index',
            'spirit:category:index']
        for url_name in url_names:
            url = reverse(url_name)
            req = RequestFactory().get(url)
            req.user = AnonymousUser()
            resp = (
                middleware.PrivateForumMiddleware(lambda req: HttpResponse(status=500))
                .process_request(req))
            self.assertIsInstance(resp, HttpResponseRedirect)
            self.assertEqual(
                resp['Location'],
                reverse(settings.LOGIN_URL) + '?next=' + url)
