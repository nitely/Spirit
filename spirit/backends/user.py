#-*- coding: utf-8 -*-

from django.contrib.auth.backends import ModelBackend

from django.contrib.auth import get_user_model


User = get_user_model()


class EmailAuthBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User._default_manager.get(email=username)

            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass