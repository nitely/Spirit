# -*- coding: utf-8 -*-

import os
import shutil
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import caches, cache

from spirit.core.conf import settings
from spirit.core.storage import spirit_storage
from spirit.topic.models import Topic
from spirit.category.models import Category
from spirit.comment.models import Comment
from spirit.topic.private.models import TopicPrivate
from spirit.topic.notification.models import TopicNotification

User = get_user_model()


def create_user(**kwargs):
    if 'username' not in kwargs:
        kwargs['username'] = "user_foo%d" % User.objects.all().count()

    if 'email' not in kwargs:
        kwargs['email'] = "%s@bar.com" % kwargs['username']

    if 'password' not in kwargs:
        kwargs['password'] = "bar"

    return User.objects.create_user(**kwargs)


def create_topic(category, **kwargs):
    if 'user' not in kwargs:
        kwargs['user'] = create_user()

    if 'title' not in kwargs:
        kwargs['title'] = "topic_foo%d" % Topic.objects.all().count()

    return Topic.objects.create(category=category, **kwargs)


def create_private_topic(**kwargs):
    assert 'category' not in kwargs, "do not pass category param"

    category = Category.objects.get(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
    topic = create_topic(category=category, **kwargs)
    return TopicPrivate.objects.create(topic=topic, user=topic.user)


def create_category(**kwargs):
    if 'title' not in kwargs:
        kwargs['title'] = "category_foo%d" % Category.objects.all().count()
    if 'sort' not in kwargs:
        kwargs['sort'] = Category.objects.all().count() + 1

    return Category.objects.create(**kwargs)


def create_subcategory(category, **kwargs):
    if 'title' not in kwargs:
        kwargs['title'] = "subcategory_foo%d" % Category.objects.all().count()

    return Category.objects.create(parent=category, **kwargs)


def create_comment(**kwargs):
    if 'comment' not in kwargs:
        kwargs['comment'] = "comment_foobar%d" % Comment.objects.all().count()
    if 'comment_html' not in kwargs:
        kwargs['comment_html'] = kwargs['comment']
    if 'user' not in kwargs:
        kwargs['user'] = create_user()
    if 'topic' not in kwargs:
        kwargs['topic'] = create_topic(create_category())
    return Comment.objects.create(**kwargs)


def create_notification(
    comment=None, user=None, is_read=True, action=None, is_active=True
):
    comment = comment or create_comment()
    user = user or create_user()
    actions = {
        'reply': TopicNotification.COMMENT,
        'mention': TopicNotification.MENTION,
        None: TopicNotification.UNDEFINED}
    notification, created = TopicNotification.create_maybe(
        comment=comment, user=user, is_read=is_read, action=actions[action])
    assert created
    if not is_active:
        notification.is_active = False
        notification.save()
    return notification

def default_categories():
    # Only public categories are included
    return Category.objects.filter(title="Uncategorized")


def login(test_case_instance, user=None, password=None):
    user = user or test_case_instance.user
    password = password or "bar"
    login_successful = test_case_instance.client.login(
        username=user.username,
        password=password)
    test_case_instance.assertTrue(login_successful)


def cache_clear():
    cache.clear()  # Default one

    for c in caches.all():
        c.clear()


def immediate_on_commit(func):
    def wrapper(*args, **kwargs):
        with mock.patch('django.db.transaction.on_commit', side_effect=lambda x: x()):
            func(*args, **kwargs)
    return wrapper


def clean_media():
    assert 'media_test' in settings.MEDIA_ROOT
    shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)


def with_test_storage(func):
    org_get_available_name = spirit_storage.get_available_name
    def get_available_name(name, **kwargs):
        name, ext = os.path.splitext(name)
        name = ''.join((name, '_test', ext))
        return org_get_available_name(name, **kwargs)
    def wrapper(*args, **kwargs):
        target = 'spirit.core.storage.spirit_storage.get_available_name'
        with mock.patch(target, get_available_name):
            func(*args, **kwargs)
        clean_media()
    return wrapper
