# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.views import redirect_to_login
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin

from .conf import settings


class XForwardedForMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR'].split(",")[-1].strip()


class PrivateForumMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not settings.ST_PRIVATE_FORUM:
            return

        if request.user.is_authenticated:
            return

        resolver_match = resolve(request.path)

        if resolver_match.app_name != 'spirit':
            return

        full_namespace = ':'.join(resolver_match.namespaces)

        if full_namespace == 'spirit:user:auth':
            return

        return redirect_to_login(
            next=request.get_full_path(),
            login_url=settings.LOGIN_URL)
