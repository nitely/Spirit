# -*- coding: utf-8 -*-

import logging

from django.db import transaction
from django.apps import apps
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.core import mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import djconfig
from PIL import Image

from spirit.user.utils import tokens
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


def _send_email(subject, message, to, unsub=None, conn=None):
    assert isinstance(to, str)
    # Subject cannot contain new lines
    subject = ''.join(subject.splitlines())
    headers = {}
    if unsub:
        headers['List-Unsubscribe'] = '<%s>' % unsub
    return mail.EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to,
        headers=headers,
        connection=conn).send()


@delayed_task
def send_email(subject, message, from_email, recipients):
    # Avoid retrying this task. It's better to log the exception
    # here instead of possibly spamming users on retry
    # We send to one recipient at the time, because otherwise
    # it'll likely get flagged as spam, or it won't reach the
    # the recipient at all
    for recipient in recipients:
        try:
            _send_email(subject, message, recipient)
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
def notify_reply(comment_id, site):
    if settings.ST_TASK_MANAGER is None:
        return
    djconfig.reload_maybe()
    Comment = apps.get_model('spirit_comment.Comment')
    Notification = apps.get_model(
        'spirit_topic_notification.TopicNotification')
    comment = (
        Comment.objects
            .get(pk=comment_id)
            .select_related('user__st', 'topic'))
    notifications = (
        Notification.objects
            .exclude(user_id=comment.user_id)
            .filter(
            topic_id=comment.topic_id,
            is_read=False,
            action=Comment.MENTION)
            .only('user_id', 'user__email'))
    # ...


@delayed_task
def notify_reply(comment_id, site):
    if settings.ST_TASK_MANAGER is None:
        return
    djconfig.reload_maybe()
    Comment = apps.get_model('spirit_comment.Comment')
    Notification = apps.get_model(
        'spirit_topic_notification.TopicNotification')
    comment = (
        Comment.objects
        .get(pk=comment_id)
        .select_related('user__st', 'topic'))
    notifications = (
        Notification.objects
        .exclude(user_id=comment.user_id)
        .filter(
            topic_id=comment.topic_id,
            is_read=False,
            action=Comment.COMMENT)
        .only('user_id', 'user__email'))
    # Since this is a task, the default language will
    # be used; we don't know what language each user prefers
    # XXX auto save user prefer/browser language in some field
    subject = _("{user} commented on {topic}").format(
        user=comment.user.st.nickname,
        topic=comment.topic.title)
    with mail.get_connection() as connection:
        for n in notifications.iterator(chunk_size=2000):
            unsub_token = tokens.unsub_token(n.user_id)
            message = render_to_string('spirit/topic/notification/email_notification.txt', {
                'site': site,
                'comment_id': comment_id,
                'unsub_token': unsub_token})
            unsub = ''.join((site, reverse(
                'spirit:user:unsubscribed',
                kwargs={'token': unsub_token})))
            try:
                _send_email(
                    subject, message,
                    to=n.user.email,
                    unsub=unsub,
                    conn=connection)
            except OSError as err:
                logger.exception(err)
                return  # bail out


@delayed_task
def clean_sessions():
    pass


@delayed_task
def backup_database():
    pass

