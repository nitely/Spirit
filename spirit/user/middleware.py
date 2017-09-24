# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging

import pytz

from django.contrib.auth import logout
from django.utils import timezone

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:  # Django < 1.10
    MiddlewareMixin = object

from ..core.conf import settings
from .models import UserProfile


__all__ = [
    'TimezoneMiddleware',
    'LastIPMiddleware',
    'LastSeenMiddleware',
    'ActiveUserMiddleware']

logger = logging.getLogger('django')


class TimezoneMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if request.user.is_authenticated():
            try:
                timezone.activate(request.user.st.timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                timezone.deactivate()
                logger.error(
                    '%s is not a valid timezone.' %
                    request.user.st.timezone)
        else:
            timezone.deactivate()


class LastIPMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        last_ip = request.META['REMOTE_ADDR'].strip()

        if request.user.st.last_ip == last_ip:
            return

        (UserProfile.objects
            .filter(user__pk=request.user.pk)
            .update(last_ip=last_ip))


class LastSeenMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        threshold = settings.ST_USER_LAST_SEEN_THRESHOLD_MINUTES * 60
        delta = timezone.now() - request.user.st.last_seen

        if delta.seconds < threshold:
            return

        (UserProfile.objects
            .filter(user__pk=request.user.pk)
            .update(last_seen=timezone.now()))


class ActiveUserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        if not request.user.is_active:
            logout(request)
