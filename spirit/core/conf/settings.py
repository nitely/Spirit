# -*- coding: utf-8 -*-

from django.conf import settings as django_settings

from . import defaults

__all__ = ['settings']


class Settings:
    """
    Get a setting from django settings or\
    Spirit's defaults. In that order
    """

    def __getattr__(self, item):
        try:
            return getattr(django_settings, item)
        except AttributeError:
            return getattr(defaults, item)


settings = Settings()
