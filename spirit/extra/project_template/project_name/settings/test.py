# -*- coding: utf-8 -*-

# THIS IS FOR DEVELOPMENT ENVIRONMENT
# DO NOT USE IT IN PRODUCTION

# This is used to test settings and urls from example directory
# with `./runtests.py example`

from __future__ import unicode_literals

from .base import *

SECRET_KEY = "TEST"

INSTALLED_APPS.extend([
    'spirit.core.tests',
])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db_test.sqlite3'),
    }
}

ROOT_URLCONF = 'example.project.urls'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_test')

STATIC_ROOT = os.path.join(BASE_DIR, 'static_test')
