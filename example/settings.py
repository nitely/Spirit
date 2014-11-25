# -*- coding: utf-8 -*-
"""
Django settings for running the example of spirit app
"""

from __future__ import unicode_literals

import os
import sys

from spirit.settings import *

# You may override spirit settings below...

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(__file__)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'change-me'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = []

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Application definition

# Extend the Spirit installed apps (notice the plus sign)
# Check out the spirit.settings.py so you do not end up with duplicate apps.
INSTALLED_APPS += (
    # 'my_app1',
    # 'my_app2',
    # 'debug_toolbar',
)

# same here, check out the spirit.settings.py
MIDDLEWARE_CLASSES += (
    # 'my_middleware1',
    # 'my_middleware2',
)

# same here
TEMPLATE_CONTEXT_PROCESSORS += (
    # 'my_template_proc1',
    # 'my_template_proc2',
)

# same here (we update the Spirit caches)
CACHES.update({
    # 'default': {
    #   'BACKEND': 'my.backend.path',
    # },
})


ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# This is used to test settings and urls from example directory
# with `./runtests.py example`

EXAMPLE = 'example' in sys.argv

if EXAMPLE:
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
        )
    # Add tests apps to installed_apps
    INSTALLED_APPS += (
        'tests',
    )
    ROOT_URLCONF = 'example.urls'

try:
    # devs must create this file to override settings
    # local_settings_sample.py is provided
    from local_settings import *
except ImportError:
    pass
