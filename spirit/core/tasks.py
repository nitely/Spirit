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


def post_commit_task(t):
    def post_commit_task_inner(*args, **kwargs):
        transaction.on_commit(lambda: t.delay(*args, **kwargs))
    return post_commit_task_inner


@post_commit_task
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
