# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import resolve


class XForwardedForMiddleware(object):

    def process_request(self, request):
        if not settings.DEBUG:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR'].split(",")[-1].strip()


class PrivateForumMiddleware(object):

    def process_request(self, request):
        if not settings.ST_PRIVATE_FORUM:
            return

        if request.user.is_authenticated():
            return

        resolver_match = resolve(request.path)

        if resolver_match.app_name != 'spirit':
            return

        full_namespace = ':'.join(resolver_match.namespaces)

        if full_namespace == 'spirit:user:auth':
            return

        return redirect_to_login(
            next=request.get_full_path(),
            login_url=settings.LOGIN_URL
        )
