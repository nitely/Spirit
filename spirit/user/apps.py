# -*- coding: utf-8 -*-

from django.apps import AppConfig


class SpiritUserConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spirit.user'
    verbose_name = "Spirit User"
    label = 'spirit_user'

    def ready(self):
        self.register_signals()

    def register_signals(self):
        from . import signals
