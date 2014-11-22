# -*- coding: utf-8 -*-
"""
Django settings for running the tests of spirit app
"""

from __future__ import unicode_literals

import os

from spirit.settings import *
from .settings_sample_dev import *

SECRET_KEY = 'change-me'

INSTALLED_APPS += (
    'tests',
)

ROOT_URLCONF = 'tests.urls'

USE_TZ = True

STATIC_URL = '/static/'