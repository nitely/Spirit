# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig


class SpiritConfig(AppConfig):

    name = 'spirit'
    verbose_name = "Spirit"

    def ready(self):
        self.register_signals()

    def register_signals(self):
        from spirit.signals import handlers
