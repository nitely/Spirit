# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import AppConfig


class SpiritAdminConfig(AppConfig):

    name = 'spirit.admin'
    verbose_name = "Spirit Admin"
    label = 'spirit_admin'

    def ready(self):
        self.register_config()

    def register_config(self):
        import djconfig
        from .forms import BasicConfigForm

        djconfig.register(BasicConfigForm)
