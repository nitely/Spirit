# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE
# YOU MAY EXTEND/OVERWRITE THE DEFAULT VALUES IN YOUR settings.py FILE

from __future__ import unicode_literals
import os

from spirit.settings import reusableapp
from spirit.settings.reusableapp import *

ST_BASE_DIR = os.path.join(os.path.dirname(__file__), '..')

#
# Django & Spirit settings defined below...
#

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
] + reusableapp.INSTALLED_APPS

# python manage.py createcachetable
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'spirit_cache',
    },
}

AUTHENTICATION_BACKENDS = [
    'spirit.user.auth.backends.UsernameAuthBackend',
    'spirit.user.auth.backends.EmailAuthBackend',
]

LOGIN_URL = 'spirit:user:auth:login'
LOGIN_REDIRECT_URL = 'spirit:user:update'

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
] + reusableapp.MIDDLEWARE_CLASSES

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


#
# Third-party apps settings defined below...
#

TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'djconfig.context_processors.config',
]
