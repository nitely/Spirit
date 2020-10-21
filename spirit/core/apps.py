# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

from .conf import settings


class SpiritCoreConfig(AppConfig):

    name = 'spirit.core'
    verbose_name = "Spirit Core"
    label = 'spirit_core'

    def ready(self):
        if not settings.ST_SITE_URL:
            raise ImproperlyConfigured('ST_SITE_URL setting not set')
