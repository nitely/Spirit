# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth import logout
from django.core.urlresolvers import resolve
from django.contrib.auth.views import redirect_to_login


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


class PrivateForumMiddleware(object):

    def process_request(self, request):
        if not settings.ST_PRIVATE_FORUM:
            return

        if request.user.is_authenticated():
            return

        resolver_match = resolve(request.path)

        if resolver_match.app_name != 'spirit':
            return

        # Namespacing /user/ would be better but breaks current urls namespace.
        url_whitelist = {'user-login',
                         'user-logout',
                         'user-register',
                         'resend-activation',
                         'registration-activation',
                         'password-reset',
                         'password-reset-done',
                         'password-reset-confirm',
                         'password-reset-complete'}

        if resolver_match.url_name in url_whitelist:
            return

        return redirect_to_login(next=request.get_full_path(),
                                 login_url=settings.LOGIN_URL)
