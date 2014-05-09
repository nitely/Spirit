#-*- coding: utf-8 -*-

from functools import wraps

from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.conf import settings


def moderator_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated():
            return redirect_to_login(next=request.get_full_path(),
                                     login_url=settings.LOGIN_URL)

        if not user.is_moderator:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper


def administrator_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated():
            return redirect_to_login(next=request.get_full_path(),
                                     login_url=settings.LOGIN_URL)

        if not user.is_administrator:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper