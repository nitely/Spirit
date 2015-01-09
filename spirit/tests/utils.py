# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.conf import settings

from spirit.models.topic import Topic
from spirit.models.category import Category
from spirit.models.comment import Comment
from spirit.models.topic_private import TopicPrivate
from spirit.models.profile import ForumProfile, PROFILE_FIELDS
from spirit.tests import factories

User = get_user_model()


def create_user(**kwargs):
    profile_kwargs = {}
    for field in PROFILE_FIELDS:
        value = kwargs.pop(field, None)
        if value:
            profile_kwargs.update({
                field: value
            })

    if 'username' not in kwargs:
        kwargs['username'] = "foo%d" % User.objects.all().count()

    if 'email' not in kwargs:
        kwargs['email'] = "%s@bar.com" % kwargs['username']

    if 'password' not in kwargs:
        kwargs['password'] = "bar"

    user = User.objects.create_user(**kwargs)
    profile_kwargs.update({
        'user': user
    })
    profile = ForumProfile.objects.create(**profile_kwargs)

    return user


def create_topic(category, **kwargs):
    if 'user' not in kwargs:
        username = "foo%d" % User.objects.all().count()
        email = "%s@bar.com" % username
        kwargs['user'] = User.objects.create_user(username=username, password="bar", email=email)

    if 'title' not in kwargs:
        kwargs['title'] = "foo%d" % Topic.objects.all().count()

    return Topic.objects.create(category=category, **kwargs)


def create_private_topic(**kwargs):
    assert 'category' not in kwargs, "do not pass category param"

    category = Category.objects.get(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
    topic = create_topic(category=category, **kwargs)
    return TopicPrivate.objects.create(topic=topic, user=topic.user)


def create_category(**kwargs):
    if 'title' not in kwargs:
        kwargs['title'] = "foo%d" % Category.objects.all().count()

    return factories.CategoryFactory(**kwargs)


def create_subcategory(category, **kwargs):
    if 'title' not in kwargs:
        kwargs['title'] = "foo%d" % Category.objects.all().count()

    return factories.CategoryFactory(parent=category, **kwargs)


def create_comment(**kwargs):
    if 'comment' not in kwargs:
        kwargs['comment'] = "foobar%d" % Comment.objects.all().count()

    if 'comment_html' not in kwargs:
        kwargs['comment_html'] = kwargs['comment']

    if 'user' not in kwargs:
        kwargs['user'] = create_user()

    return factories.CommentFactory(**kwargs)


def login(test_case_instance, user=None, password=None):
    user = user or test_case_instance.user
    password = password or "bar"
    login_successful = test_case_instance.client.login(username=user.username, password=password)
    test_case_instance.assertTrue(login_successful)
