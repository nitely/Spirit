# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.db import transaction

try:
    # TODO: remove this try block.
    from celery.decorators import task
except ImportError:
    task = None


if not hasattr(settings, 'BROKER_URL'):
    def task(f):
        f.delay = f
        return f


def delayed_task(t):
    def delayed_task_inner(*args, **kwargs):
        transaction.on_commit(lambda: t.delay(*args, **kwargs))
    return delayed_task_inner


@delayed_task
def send_notification():
    pass


@delayed_task
def backup_database():
    pass


@delayed_task
def search_index_update():
    pass


@delayed_task
def clean_sessions():
    pass
