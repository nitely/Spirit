#-*- coding: utf-8 -*-

# MINIMAL CONFIGURATION FOR PRODUCTION ENV

DEBUG = False

TEMPLATE_DEBUG = False

# https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (('John', 'john@example.com'), )

# Secret key generator: https://djskgen.herokuapp.com/
SECRET_KEY = ''

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.example.com', ]

# https://docs.djangoproject.com/en/dev/ref/settings/#databases
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