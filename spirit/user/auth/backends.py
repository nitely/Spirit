# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from ...core.conf import settings

User = get_user_model()


class EmailAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # TODO: authenticate when multiple users are returned
        if settings.ST_CASE_INSENSITIVE_EMAILS:
            username = username.lower()

        try:
            user = User._default_manager.get(email=username)

            if user.check_password(password):
                return user
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            pass

    def get_user(self, user_id):
        # This is called if the user
        # get authenticated with email
        try:
            return (
                User._default_manager
                    .select_related('st')
                    .get(pk=user_id))
        except User.DoesNotExist:
            pass


class UsernameAuthBackend(ModelBackend):
    # TODO: test!

    def get_user(self, user_id):
        try:
            return (
                User._default_manager
                    .select_related('st')
                    .get(pk=user_id))
        except User.DoesNotExist:
            pass
