# -*- coding: utf-8 -*-

# MINIMAL CONFIGURATION FOR PRODUCTION ENV

# Create your own prod_local.py
# import * this module there and use it like this:
# python manage.py runserver --settings={{ project_name }}.settings.prod_local

from __future__ import unicode_literals

from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#admins
ADMINS = (('John', 'john@example.com'), )

SECRET_KEY = os.environ.get("SECRET_KEY", '{{ secret_key }}')

# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.example.com', ]

# You can change this to something like 'MyForum <noreply@example.com>'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'  # Django default
SERVER_EMAIL = DEFAULT_FROM_EMAIL  # For error notifications

# Email sending timeout
EMAIL_TIMEOUT = 20  # Default is None (infinite)

# Extend the Spirit installed apps
# Check out the .base.py file for more examples
INSTALLED_APPS.extend([
    # 'my_app1',
])

# Database
# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mydatabase',
        'USER': 'mydatabaseuser',
        'PASSWORD': 'mypassword',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# These are all the languages Spirit provides.
# https://www.transifex.com/projects/p/spirit/
gettext_noop = lambda s: s
LANGUAGES = [
    ('de', gettext_noop('German')),
    ('en', gettext_noop('English')),
    ('es', gettext_noop('Spanish')),
    ('fr', gettext_noop('French')),
    ('hu', gettext_noop('Hungarian')),
    ('it', gettext_noop('Italian')),
    ('lt', gettext_noop('Lithuanian')),
    ('pl', gettext_noop('Polish')),
    ('pl-pl', gettext_noop('Poland Polish')),
    ('ru', gettext_noop('Russian')),
    ('sv', gettext_noop('Swedish')),
    ('tr', gettext_noop('Turkish')),
    ('zh-hans', gettext_noop('Simplified Chinese')),
]

# Default language
LANGUAGE_CODE = 'en'

# Append the MD5 hash of the file’s content to the filename
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
