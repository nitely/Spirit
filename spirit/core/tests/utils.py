# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.cache import caches, cache

from ...core.conf import settings
from ...topic.models import Topic
from ...category.models import Category
from ...comment.models import Comment
from ...topic.private.models import TopicPrivate

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

    return Comment.objects.create(**kwargs)


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
