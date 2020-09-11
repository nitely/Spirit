# -*- coding: utf-8 -*-

import logging

from django.db import transaction
from django.core.mail import send_mail
from django.apps import apps

from .conf import settings
from . import signals

logger = logging.getLogger(__name__)


# XXX support custom task manager __import__('foo.task')?
def task_manager(tm):
    if tm == 'celery':
        from celery import shared_task
        def task(t):
            t = shared_task(t)
            def _task(*args, **kwargs):
                print('delay')
                return t.delay(*args, **kwargs)
            return _task
    elif tm == 'huey':
        from huey.contrib.djhuey import db_task
        task = db_task()
    else:
        assert tm is None
        def task(t):
            return t

    return task

task = task_manager(settings.ST_TASK_MANAGER)


def delayed_task(t):
    t = task(t)  # wrap at import time
    def delayed_task_inner(*args, **kwargs):
        transaction.on_commit(lambda: t(*args, **kwargs))
    return delayed_task_inner


@delayed_task
def send_email(subject, message, from_email, recipients):
    # Avoid retrying this task. It's better to log the exception
    # here instead of possibly spamming users on retry
    # We send to one recipient at the time, because otherwise
    # it'll likely get flagged as spam, or it won't reach the
    # the recipient at all
    for recipient in recipients:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[recipient])
        except OSError as err:
            logger.exception(err)


@delayed_task
def backup_database():
    pass


# XXX update everything every 24hs to
#     update deleted categories
@delayed_task
def search_index_update(topic_pk):
    # Indexing is too expensive; skip if
    # there's no dedicated task manager
    if settings.ST_TASK_MANAGER is None:
        return
    Topic = apps.get_model('spirit_topic.Topic')
    signals.search_index_update.send(
        sender=Topic,
        instance=Topic.objects.get(pk=topic_pk))


@delayed_task
def clean_sessions():
    pass
