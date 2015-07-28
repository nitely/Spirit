# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig


class SpiritUserConfig(AppConfig):

    name = 'spirit.user'
    verbose_name = "Spirit User"
    label = 'spirit_user'

    def ready(self):
        self.register_signals()

    def register_signals(self):
        from . import signals
