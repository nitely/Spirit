# -*- coding: utf-8 -*-

# THIS IS FOR DEVELOPMENT ENVIRONMENT
# DO NOT USE IT IN PRODUCTION

# Create your own dev_local.py
# import * this module there and use it like this:
# python manage.py runserver --settings={{ project_name }}.settings.dev_local

from .base import *


DEBUG = True

TEMPLATES[0]['OPTIONS']['debug'] = True
# TEMPLATES[0]['OPTIONS']['string_if_invalid'] = '\{\{%s\}\}'  # Some Django templates relies on this being the default

ADMINS = (('John', 'john@example.com'), )  # Log email to console when DEBUG = False

SECRET_KEY = "DEV"

ALLOWED_HOSTS = ['127.0.0.1', ]

# INSTALLED_APPS.extend([
#    'debug_toolbar',
#    'huey.contrib.djhuey',
# ])

# Database
# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ST_TASK_MANAGER = 'huey'

HUEY = {
    'huey_class': 'huey.SqliteHuey',
    'name': 'spirit',
    'filename': os.path.join(BASE_DIR, 'huey.sqlite3'),
    'immediate_use_memory': False,
    'immediate': False,
    'utc': True,
    'connection': {},
    'consumer': {
        'workers': 3,
        'worker_type': 'process',
        'initial_delay': 0.1,
        'backoff': 1.15,
        'max_delay': 10.0,
        'scheduler_interval': 1,
        'periodic': True,
        'check_worker_health': True,
        'health_check_interval': 1,
    }
}
