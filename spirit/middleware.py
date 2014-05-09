#-*- coding: utf-8 -*-

import pytz

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth import logout


User = get_user_model()


class XForwardedForMiddleware(object):

    def process_request(self, request):
        if not settings.DEBUG:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR'].split(",")[-1].strip()


class TimezoneMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            timezone.activate(request.user.timezone)
        else:
            timezone.deactivate()


class LastIPMiddleware(object):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        last_ip = request.META['REMOTE_ADDR'].strip()

        if request.user.last_ip == last_ip:
            return

        User.objects.filter(pk=request.user.pk)\
            .update(last_ip=last_ip)


class LastSeenMiddleware(object):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        threshold = settings.ST_USER_LAST_SEEN_THRESHOLD_MINUTES * 60
        delta = timezone.now() - request.user.last_seen

        if delta.seconds < threshold:
            return

        User.objects.filter(pk=request.user.pk)\
            .update(last_seen=timezone.now())


class ActiveUserMiddleware(object):

    def process_request(self, request):
        if not request.user.is_authenticated():
            return

        if not request.user.is_active:
           logout(request)