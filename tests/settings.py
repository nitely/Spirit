# -*- coding: utf-8 -*-
"""
Django settings for running the tests of spirit app
"""

from __future__ import unicode_literals

import os

from spirit.settings import *


SECRET_KEY = 'TEST'

INSTALLED_APPS += (
    'tests',
)

ROOT_URLCONF = 'tests.urls'

USE_TZ = True

STATIC_URL = '/static/'

DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', ]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db_test.sqlite3'),
    }
}

CACHES.update({
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
})

# speedup tests requiring login
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Keep templates in memory to speedup tests
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)
