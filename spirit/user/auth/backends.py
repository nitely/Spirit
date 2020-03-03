# -*- coding: utf-8 -*-

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from ...core.conf import settings

User = get_user_model()


class _SpiritBackend(ModelBackend):

    def get_user(self, user_id):
        try:
            return (
                User._default_manager
                .select_related('st')
                .get(pk=user_id))
        except User.DoesNotExist:
            pass


class EmailAuthBackend(_SpiritBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # TODO: authenticate when multiple users are returned
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if settings.ST_CASE_INSENSITIVE_EMAILS:
            username = username.lower()

        try:
            user = User._default_manager.get(email=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            User().set_password(password)
        else:
            if (user.check_password(password) and
                    self.user_can_authenticate(user)):
                return user


class UsernameAuthBackend(_SpiritBackend):
    # TODO: test!

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if settings.ST_CASE_INSENSITIVE_USERNAMES:
            username = username.lower()
        return super(UsernameAuthBackend, self).authenticate(
            request, username=username, password=password, **kwargs)
