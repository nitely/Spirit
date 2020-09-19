# -*- coding: utf-8 -*-

import logging

from django.db import transaction
from django.core.mail import send_mail
from django.apps import apps
from django.core.management import call_command
from django.contrib.auth import get_user_model

from PIL import Image

from .conf import settings
from .storage import spirit_storage
from . import signals
from .utils.tasks import avatars

logger = logging.getLogger(__name__)


# XXX support custom task manager __import__('foo.task')?
def task_manager(tm):
    if tm == 'celery':
        from celery import shared_task
        def task(t):
            t = shared_task(t)
            def _task(*args, **kwargs):
                return t.delay(*args, **kwargs)
            return _task
        return task
    if tm == 'huey':
        from huey.contrib.djhuey import db_task
        return db_task()
    assert tm is None
    return lambda t: t

task = task_manager(settings.ST_TASK_MANAGER)


def periodic_task_manager(tm):
    if tm == 'huey':
        from huey import crontab
        from huey.contrib.djhuey import db_periodic_task
        def periodic_task(hours):
            return db_periodic_task(crontab(
                minute='0', hour='*/{}'.format(hours)))
        return periodic_task
    assert tm in ('celery', None)
    def fake_periodic_task(*args, **kwargs):
        return task_manager(tm)
    return fake_periodic_task

periodic_task = periodic_task_manager(settings.ST_TASK_MANAGER)


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
            return  # bail out


@delayed_task
def search_index_update(topic_pk):
    # Indexing is too expensive; bail if
    # there's no dedicated task manager
    if settings.ST_TASK_MANAGER is None:
        return
    Topic = apps.get_model('spirit_topic.Topic')
    signals.search_index_update.send(
        sender=Topic,
        instance=Topic.objects.get(pk=topic_pk))


@periodic_task(hours=settings.ST_SEARCH_INDEX_UPDATE_HOURS)
def full_search_index_update():
    age = settings.ST_SEARCH_INDEX_UPDATE_HOURS
    call_command("update_index", age=age)


@delayed_task
def make_avatars(user_id):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    user.st.avatar.open()
    image = Image.open(user.st.avatar)
    image = avatars.crop_max_square(image)
    big_avatar = avatars.thumbnail(image, 300)
    # delete original even for overwrite storage,
    # as it may have other extension
    user.st.avatar.delete()
    user.st.avatar.save('pic.jpg', big_avatar)
    user.st.save()
    small_avatar = avatars.thumbnail(image, 100)
    spirit_storage.save(
        user.st.small_avatar_name(), small_avatar)


@delayed_task
def clean_sessions():
    pass


@delayed_task
def backup_database():
    pass

