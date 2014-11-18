# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings

try:
    # TODO: remove this try block.
    from celery.decorators import task
except ImportError:
    task = None


if not hasattr(settings, 'BROKER_URL'):
    def task(f):
        f.delay = f
        return f


@task
def send_notification():
    pass


@task
def backup_database():
    pass


@task
def search_index_update():
    pass


@task
def clean_sessions():
    pass
