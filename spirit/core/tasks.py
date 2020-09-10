# -*- coding: utf-8 -*-

import logging

from django.db import transaction
from django.core.mail import send_mail

from spirit.core.conf import settings

logger = logging.getLogger(__name__)


if settings.ST_TASK_MANAGER == 'celery':
    from celery import shared_task

    def task(t):
        t = shared_task(t)
        def _task(*args, **kwargs):
            return t.delay(*args, **kwargs)
        return _task

elif settings.ST_TASK_MANAGER == 'huey':
    from huey.contrib.djhuey import task
else:
    assert settings.ST_TASK_MANAGER is None
    def task(t):
        return t


def delayed_task(t):
    t = task(t)
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


@delayed_task
def search_index_update():
    pass


@delayed_task
def clean_sessions():
    pass
