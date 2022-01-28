# -*- coding: utf-8 -*-

# MINIMAL CONFIGURATION FOR PRODUCTION ENV

# Create your own prod_local.py
# import * this module there and use it like this:
# python manage.py runserver --settings={{ project_name }}.settings.prod_local

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
    # 'huey.contrib.djhuey',
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
    ('ky', gettext_noop('Kyrgyz')),
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

# Celery is optional, Huey can be used instead
# https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html
# https://docs.celeryproject.org/en/latest/userguide/configuration.html
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULE = {
    'notify_weekly': {
        'task': 'spirit.core.tasks.notify_weekly',
        'schedule': 3600 * 24 * 7  # run once every week
        # 'schedule': crontab(hour=0, minute=0, day_of_week='sun')
    },
    'full_search_index_update': {
        'task': 'spirit.core.tasks.full_search_index_update',
        'schedule': 3600 * 24  # run once every 24hs
    }
}

# Huey
# https://huey.readthedocs.io/en/latest/django.html
HUEY = {
    'huey_class': 'huey.RedisHuey',
    'name': 'spirit',
    'immediate_use_memory': False,
    'immediate': False,
    'utc': True,
    'blocking': True,
    'connection': {
        'host': 'localhost',
        'port': 6379,
        'db': 0,
        'max_connections': 500,  # Pooling
        # ... tons of other options, see redis-py for details.
        # huey-specific connection parameters.
        'read_timeout': 1,
        'url': None,  # Allow Redis config via a DSN.
    },
    'consumer': {
        'workers': os.cpu_count() * 2 + 1,
        'worker_type': 'thread',
        'initial_delay': 0.1,
        'backoff': 1.15,
        'max_delay': 10.0,
        'scheduler_interval': 1,
        'periodic': True,
        'check_worker_health': True,
        'health_check_interval': 1,
    }
}

# https://spirit.readthedocs.io/en/latest/settings.html#spirit.core.conf.defaults.ST_SITE_URL
ST_SITE_URL = 'https://example.com/'

# If using elasticsearch, this fixes:
# https://github.com/django-haystack/django-haystack/issues/1057
ELASTICSEARCH_DEFAULT_NGRAM_SEARCH_ANALYZER = 'standard'
