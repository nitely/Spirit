# -*- coding: utf-8 -*-

# Celery is optional, Huey can be used instead
# Read the Celery docs to configure it
# https://docs.celeryproject.org/en/latest/django/first-steps-with-django.html

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ project_name }}.settings.prod")
app = Celery('{{ project_name }}')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
