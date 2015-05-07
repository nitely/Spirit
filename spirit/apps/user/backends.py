# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


User = get_user_model()


class EmailAuthBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        # TODO: authenticate when multiple users are returned
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
            return User._default_manager\
                .select_related('st')\
                .get(pk=user_id)
        except User.DoesNotExist:
            pass


class UsernameAuthBackend(ModelBackend):
    # TODO: test!

    def get_user(self, user_id):
        try:
            return User._default_manager\
                .select_related('st')\
                .get(pk=user_id)
        except User.DoesNotExist:
            pass