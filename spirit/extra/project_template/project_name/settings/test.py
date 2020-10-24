# -*- coding: utf-8 -*-

"""
Django settings for running the tests of spirit app
"""

from .base import *


SECRET_KEY = 'TEST'

INSTALLED_APPS += [
    'spirit.core.tests'
]

if bool(int(os.getenv('ST_INSTALL_HUEY', True))):
    INSTALLED_APPS.append('huey.contrib.djhuey')

ROOT_URLCONF = 'project.project.urls'

USE_TZ = True

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media_test')

STATIC_ROOT = os.path.join(BASE_DIR, 'static_test')

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', ]

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
    'st_rate_limit': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'spirit_rl_cache',
        'TIMEOUT': None
    }
})

# speedup tests requiring login
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TEMPLATES[0]['OPTIONS']['debug'] = True

ST_EXTENDED_FONT = True
ST_RATELIMIT_CACHE = 'st_rate_limit'
ST_UPLOAD_FILE_ENABLED = bool(int(os.getenv('ST_UPLOAD_FILE_ENABLED', True)))
ST_ORDERED_CATEGORIES = True
ST_TASK_MANAGER = os.getenv('ST_TASK_MANAGER', None)
ST_SITE_URL = 'https://example.com/'
HUEY = {
    'name': 'test',
    'immediate': True
}
CELERY_ALWAYS_EAGER = True
CELERY_TASK_ALWAYS_EAGER = True

HAYSTACK_CONNECTIONS['default']['STORAGE'] = 'ram'
HAYSTACK_LIMIT_TO_REGISTERED_MODELS = False

LOGGING['loggers']['celery']['level'] = 'ERROR'
LOGGING['loggers']['huey']['level'] = 'ERROR'
