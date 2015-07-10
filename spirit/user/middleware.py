# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import logout
from django.utils import timezone

from .models import UserProfile


class TimezoneMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            timezone.activate(request.user.st.timezone)
        else:
            timezone.deactivate()


class LastIPMiddleware(object):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        last_ip = request.META['REMOTE_ADDR'].strip()

        if request.user.st.last_ip == last_ip:
            return

        UserProfile.objects\
            .filter(user__pk=request.user.pk)\
            .update(last_ip=last_ip)


class LastSeenMiddleware(object):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        threshold = settings.ST_USER_LAST_SEEN_THRESHOLD_MINUTES * 60
        delta = timezone.now() - request.user.st.last_seen

        if delta.seconds < threshold:
            return

        UserProfile.objects\
            .filter(user__pk=request.user.pk)\
            .update(last_seen=timezone.now())


class ActiveUserMiddleware(object):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        if not request.user.is_active:
            logout(request)