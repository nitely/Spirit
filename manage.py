#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings_test_runner'

from django.core import management
if __name__ == "__main__":
    management.execute_from_command_line()
