# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime
import hashlib

from django.test import TestCase, override_settings
from django.urls import reverse
from django.template import Template, Context
from django.utils import timezone

from djconfig.utils import override_djconfig

from ...core.conf import settings
from ...core.tests import utils
from ...category.models import Category
from .models import TopicPrivate
from .forms import (
    TopicForPrivateForm,
    TopicPrivateInviteForm,
    TopicPrivateManyForm,
    TopicPrivateJoinForm)
from .tags import render_invite_form
from ..models import Topic
from ...comment.bookmark.models import CommentBookmark
from .. import utils as utils_topic
from ..notification.models import TopicNotification
from .utils import notify_access
from . import views as private_views


class TopicPrivateViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()

    @override_settings(ST_TESTS_RATELIMIT_NEVER_EXPIRE=True)
    def test_private_publish(self):
        """
        POST, create private topic
        """
        self.assertEqual(len(Topic.objects.all()), 0)

        utils.login(self)
        form_data = {'comment': 'foo', 'title': 'foobar', 'users': self.user2.username}
        response = self.client.post(reverse('spirit:topic:private:publish'), form_data)
        private = TopicPrivate.objects.last()
        expected_url = private.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(len(Topic.objects.all()), 1)

        # ratelimit
        form_data['title'] = 'new foobar'
        form_data['comment'] = 'new foo'
        response = self.client.post(reverse('spirit:topic:private:publish'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Topic.objects.all()), 1)

        response = self.client.get(reverse('spirit:topic:private:publish'))
        self.assertEqual(response.status_code, 200)

    @override_settings(ST_TESTS_RATELIMIT_NEVER_EXPIRE=True)
    def test_private_publishvalidate(self):
        """
        Should validate all forms even when errors
        """
        self.assertEqual(len(Topic.objects.all()), 0)

        utils.login(self)
        no_data = {}
        response = self.client.post(reverse('spirit:topic:private:publish'), no_data)
        self.assertEqual(len(Topic.objects.all()), 0)
        self.assertTrue(bool(response.context['tform'].errors))
        self.assertTrue(bool(response.context['cform'].errors))
        self.assertTrue(bool(response.context['tpform'].errors))
        self.assertEqual(len(list(response.context['messages'])), 0)

        # No rate-limit
        form_data = {'comment': 'foo', 'title': 'foobar', 'users': self.user2.username}
        self.client.post(reverse('spirit:topic:private:publish'), form_data)
        self.assertEqual(len(Topic.objects.all()), 1)

    def test_private_publish_create_notifications(self):
        """
        Should create notifications for invited members
        """
        utils.login(self)
        user = utils.create_user()
        form_data = {'comment': 'foo', 'title': 'foobar', 'users': [user.username, ]}
        response = self.client.post(reverse('spirit:topic:private:publish'),
                                    form_data)
        self.assertEqual(response.status_code, 302)

        topic_private = TopicPrivate.objects.last()
        self.assertEqual(len(TopicNotification.objects.filter(topic=topic_private.topic)), 2)
        self.assertEqual(len(TopicNotification.objects.filter(topic=topic_private.topic, user=user)), 1)
        self.assertEqual(len(TopicNotification.objects.filter(topic=topic_private.topic, user=self.user)), 1)

    def test_private_publish_user(self):
        """
        create private topic with user as initial value
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:topic:private:publish', kwargs={'user_id': self.user2.pk, }))
        self.assertEqual(response.context['tpform'].initial['users'], [self.user2.username, ])

    @override_settings(ST_DOUBLE_POST_THRESHOLD_MINUTES=10)
    def test_private_publish_double_post(self):
        """
        Should prevent double posts
        """
        utils.login(self)
        category_private = Category.objects.get(
            pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        topic_title = 'title foobar'

        # First post
        self.client.post(
            reverse('spirit:topic:private:publish'),
            {'comment': 'foo', 'title': topic_title, 'users': [self.user2.username]})
        self.assertEqual(len(Topic.objects.all()), 1)

        # Double post
        utils.cache_clear()  # Clear rate limit
        response = self.client.post(
            reverse('spirit:topic:private:publish'),
            {'comment': 'new foo', 'title': topic_title, 'users': [self.user2.username]})
        self.assertEqual(len(Topic.objects.all()), 1)  # Prevented!

        self.assertRedirects(
            response,
            expected_url=category_private.get_absolute_url(),
            status_code=302,
            target_status_code=200)

        # New post
        utils.cache_clear()  # Clear rate limit
        self.client.post(
            reverse('spirit:topic:private:publish'),
            {'comment': 'foo', 'title': 'new topic', 'users': [self.user2.username]})
        self.assertEqual(len(Topic.objects.all()), 2)

    def test_private_detail(self):
        """
        private topic detail
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user)

        comment1 = utils.create_comment(topic=private.topic)
        comment2 = utils.create_comment(topic=private.topic)

        category = utils.create_category()
        topic2 = utils.create_topic(category=category)
        utils.create_comment(topic=topic2)

        response = self.client.get(reverse('spirit:topic:private:detail', kwargs={'topic_id': private.topic.pk,
                                                                            'slug': private.topic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['topic'], private.topic)
        self.assertEqual(list(response.context['comments']), [comment1, comment2])

    @override_djconfig(comments_per_page=2)
    def test_private_detail_view_paginate(self):
        """
        should display topic with comments, page 1
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user)

        comment1 = utils.create_comment(topic=private.topic)
        comment2 = utils.create_comment(topic=private.topic)
        utils.create_comment(topic=private.topic)  # comment3

        response = self.client.get(reverse('spirit:topic:private:detail', kwargs={'topic_id': private.topic.pk,
                                                                            'slug': private.topic.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['topic'], private.topic)
        self.assertEqual(list(response.context['comments']), [comment1, comment2])

    def test_topic_private_detail_viewed(self):
        """
        Calls utils.topic_viewed
        """
        def mocked_topic_viewed(request, topic):
            self._user = request.user
            self._topic = topic

        org_viewed, utils_topic.topic_viewed = utils_topic.topic_viewed, mocked_topic_viewed
        try:
            utils.login(self)
            category = utils.create_category()
            topic = utils.create_topic(category=category, user=self.user)
            response = self.client.get(reverse('spirit:topic:detail', kwargs={'pk': topic.pk, 'slug': topic.slug}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self._topic, topic)
            self.assertEqual(self._user, self.user)
        finally:
            utils_topic.topic_viewed = org_viewed

    def test_private_access_create(self):
        """
        private topic access creation
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user)
        utils.create_comment(topic=private.topic)
        form_data = {'user': self.user2.username, }
        response = self.client.post(reverse('spirit:topic:private:access-create', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        expected_url = private.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertEqual(len(TopicPrivate.objects.filter(user=self.user2, topic=private.topic)), 1)

    def test_private_access_create_invalid(self):
        """
        Only the topic owner should be able to invite
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user2)
        TopicPrivate.objects.create(user=self.user, topic=private.topic)
        user = utils.create_user()
        form_data = {'user': user.username, }
        response = self.client.post(reverse('spirit:topic:private:access-create', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_private_access_create_notify_access(self):
        """
        notify_access
        """
        def mocked_notify_access(user, topic_private):
            self._user = user
            self._topic_private = topic_private

        org_access, private_views.notify_access = private_views.notify_access, mocked_notify_access
        try:
            utils.login(self)
            private = utils.create_private_topic(user=self.user)
            form_data = {'user': self.user2.username, }
            response = self.client.post(reverse('spirit:topic:private:access-create', kwargs={'topic_id': private.topic.pk, }),
                                        form_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(self._topic_private, TopicPrivate.objects.last())
            self.assertEqual(self._user, self.user2)
        finally:
            private_views.notify_access = org_access

    def test_private_access_delete(self):
        """
        private topic access deletion
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user)
        private2 = TopicPrivate.objects.create(user=self.user2, topic=private.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:private:access-remove', kwargs={'pk': private2.pk, }),
                                    form_data)
        expected_url = private.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

    def test_private_access_delete_invalid(self):
        """
        Only the topic owner should be able to remove accesses
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user2)
        TopicPrivate.objects.create(user=self.user, topic=private.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:private:access-remove', kwargs={'pk': private.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_private_access_delete_leave(self):
        """
        user should be able to remove himself
        """
        utils.login(self)
        private = utils.create_private_topic(user=self.user2)
        private2_leave = TopicPrivate.objects.create(user=self.user, topic=private.topic)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:private:access-remove', kwargs={'pk': private2_leave.pk, }),
                                    form_data)
        expected_url = reverse("spirit:topic:private:index")
        self.assertRedirects(response, expected_url, status_code=302)

    def test_private_list(self):
        """
        private topic list
        """
        private = utils.create_private_topic(user=self.user)
        # dont show private topics from other users
        TopicPrivate.objects.create(user=self.user2, topic=private.topic)
        # dont show topics from other categories
        category = utils.create_category()
        utils.create_topic(category, user=self.user)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:private:index'))
        self.assertEqual(list(response.context['topics']), [private.topic, ])

    def test_private_list_order_topics(self):
        """
        private topic list ordered by last active
        """
        private_a = utils.create_private_topic(user=self.user)
        private_b = utils.create_private_topic(user=self.user)
        private_c = utils.create_private_topic(user=self.user)

        Topic.objects.filter(pk=private_a.topic.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))
        Topic.objects.filter(pk=private_c.topic.pk).update(last_active=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:private:index'))
        self.assertEqual(list(response.context['topics']), [private_b.topic, private_c.topic, private_a.topic])

    def test_private_list_bookmarks(self):
        """
        private topic list with bookmarks
        """
        private = utils.create_private_topic(user=self.user)
        bookmark = CommentBookmark.objects.create(topic=private.topic, user=self.user)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:private:index'))
        self.assertEqual(list(response.context['topics']), [private.topic, ])
        self.assertEqual(response.context['topics'][0].bookmark, bookmark)

    @override_djconfig(topics_per_page=1)
    def test_private_list_paginated(self):
        """
        private topic list paginated
        """
        utils.create_private_topic(user=self.user)
        private = utils.create_private_topic(user=self.user)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:private:index'))
        self.assertEqual(list(response.context['topics']), [private.topic, ])

    def test_private_join(self):
        """
        private topic join
        """
        private = utils.create_private_topic(user=self.user)
        utils.create_comment(topic=private.topic)
        private.delete()

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:private:join', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        expected_url = private.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

        response = self.client.get(reverse('spirit:topic:private:join', kwargs={'topic_id': private.topic.pk, }))
        self.assertEqual(response.status_code, 200)

    def test_private_join_invalid_regular_topic(self):
        """
        Only topics from the category private can be rejoined
        """
        category = utils.create_category()
        topic = utils.create_topic(category, user=self.user)

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:private:join', kwargs={'topic_id': topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_private_join_invalid_not_owner(self):
        """
        Only topic creators/owners can rejoin
        """
        private = utils.create_private_topic(user=self.user2)

        utils.login(self)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:private:join', kwargs={'topic_id': private.topic.pk, }),
                                    form_data)
        self.assertEqual(response.status_code, 404)

    def test_private_join_access_notify_access(self):
        """
        notify_access
        """
        def mocked_notify_access(user, topic_private):
            self._user = user
            self._topic_private = topic_private

        org_access, private_views.notify_access = private_views.notify_access, mocked_notify_access
        try:
            private = utils.create_private_topic(user=self.user)
            private.delete()

            utils.login(self)
            form_data = {}
            response = self.client.post(reverse('spirit:topic:private:join', kwargs={'topic_id': private.topic.pk, }),
                                        form_data)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(self._topic_private, TopicPrivate.objects.last())
            self.assertEqual(self._user, self.user)
        finally:
            private_views.notify_access = org_access

    def test_private_created_list(self):
        """
        private topic created list, shows only the private topics the user is no longer participating
        """
        category = utils.create_category()
        utils.create_topic(category, user=self.user)
        # it's the owner, left the topic
        private = utils.create_private_topic(user=self.user)
        private.delete()
        # has access and is the owner
        utils.create_private_topic(user=self.user)
        # does not has access
        utils.create_private_topic(user=self.user2)
        # has access but it's not owner
        private4 = utils.create_private_topic(user=self.user2)
        TopicPrivate.objects.create(user=self.user, topic=private4.topic)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:private:index-author'))
        self.assertEqual(list(response.context['topics']), [private.topic, ])

    def test_private_created_list_order_topics(self):
        """
        private topic created list ordered by last active
        """
        private_a = utils.create_private_topic(user=self.user)
        private_b = utils.create_private_topic(user=self.user)
        private_c = utils.create_private_topic(user=self.user)
        private_a.delete()
        private_b.delete()
        private_c.delete()

        Topic.objects.filter(pk=private_a.topic.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))
        Topic.objects.filter(pk=private_c.topic.pk).update(last_active=timezone.now() - datetime.timedelta(days=5))

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:private:index-author'))
        self.assertEqual(list(response.context['topics']), [private_b.topic, private_c.topic, private_a.topic])

    @override_djconfig(topics_per_page=1)
    def test_private_created_list_paginate(self):
        """
        private topic created list paginated
        """
        private = utils.create_private_topic(user=self.user)
        private.delete()
        private2 = utils.create_private_topic(user=self.user)
        private2.delete()

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:private:index-author'))
        self.assertEqual(list(response.context['topics']), [private2.topic, ])


class TopicPrivateFormTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()

    def test_private_publish(self):
        """
        create simple topic
        """
        form_data = {'title': 'foo', }
        form = TopicForPrivateForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_private_publish_category(self):
        """
        Should return the private category
        """
        category_private = Category.objects.get(
            pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        form = TopicForPrivateForm()
        self.assertEqual(form.category, category_private)
        self.assertEqual(form.category, category_private)  # Cached

    def test_private_publish_get_topic_hash(self):
        """
        Should return the topic hash
        """
        category_private = Category.objects.get(
            pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        title = 'title foobar'
        form = TopicForPrivateForm(data={'title': title})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.get_topic_hash(),
            hashlib.md5(
                '{}category-{}'
                .format(title, category_private.pk)
                .encode('utf-8')).hexdigest())

    def test_private_publish_get_topic_hash_from_field(self):
        """
        Should return the topic hash from form field
        """
        topic_hash = '1' * 32
        form = TopicForPrivateForm(
            data={
                'title': 'foobar',
                'topic_hash': topic_hash})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_topic_hash(), topic_hash)

    def test_private_create_many(self):
        """
        create many private topics accesses
        """
        users = '%s, %s' % (self.user.username, self.user2.username)
        form_data = {'users': users, }
        form = TopicPrivateManyForm(self.user, data=form_data)
        self.assertEqual(form.is_valid(), True)

        category = Category.objects.get(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        topic = utils.create_topic(category=category, user=self.user)
        form.topic = topic
        privates_saved = form.save_m2m()
        self.assertEqual(len(privates_saved), 2)
        privates = TopicPrivate.objects.all()
        self.assertEqual([p.user.pk for p in privates], [self.user2.pk, self.user.pk])

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=True)
    def test_private_invite_case_insensitive(self):
        user1 = utils.create_user(username='UnIQuEfOo')
        self.assertNotEqual(
            user1.username, user1.username.upper())
        form_data = {'user': user1.username.upper()}
        private = utils.create_private_topic(user=self.user)
        form = TopicPrivateInviteForm(private.topic, data=form_data)
        self.assertEqual(form.is_valid(), True)

        # regular username should still work
        form_data = {'user': user1.username}
        private = utils.create_private_topic(user=self.user)
        form = TopicPrivateInviteForm(private.topic, data=form_data)
        self.assertEqual(form.is_valid(), True)

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=False)
    def test_private_invite_case_insensitive_off(self):
        user1 = utils.create_user(username='UnIQuEfOo')
        self.assertNotEqual(
            user1.username, user1.username.upper())
        form_data = {'user': user1.username.upper()}
        private = utils.create_private_topic(user=self.user)
        form = TopicPrivateInviteForm(private.topic, data=form_data)
        self.assertEqual(form.is_valid(), False)

        # regular username should still work
        form_data = {'user': user1.username}
        private = utils.create_private_topic(user=self.user)
        form = TopicPrivateInviteForm(private.topic, data=form_data)
        self.assertEqual(form.is_valid(), True)

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=True)
    def test_private_create_many_case_insensitive(self):
        """
        create many private topics accesses
        """
        user1 = utils.create_user(username='UnIQuEfOo')
        user2 = utils.create_user(username='uniquebar')
        self.assertNotEqual(
            user1.username, user1.username.upper())
        self.assertEqual(
            user2.username, 'uniquebar')
        users = '%s, %s' % (
            user1.username.upper(), 'uniquebar')
        form_data = {'users': users}
        form = TopicPrivateManyForm(self.user, data=form_data)
        self.assertEqual(form.is_valid(), True)

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=False)
    def test_private_create_many_case_insensitive_off(self):
        """
        create many private topics accesses
        """
        user1 = utils.create_user(username='UnIQuEfOo')
        user2 = utils.create_user(username='uniquebar')
        self.assertNotEqual(
            user1.username, user1.username.upper())
        self.assertEqual(
            user2.username, 'uniquebar')
        users = '%s, %s' % (
            user1.username.upper(), 'uniquebar')
        form_data = {'users': users}
        form = TopicPrivateManyForm(self.user, data=form_data)
        self.assertEqual(form.is_valid(), False)

        users = 'UnIQuEfOo, uniquebar'
        form_data = {'users': users}
        form = TopicPrivateManyForm(self.user, data=form_data)
        print(form.errors)
        self.assertEqual(form.is_valid(), True)

    def test_private_create(self):
        """
        create single private topic access
        """
        category = Category.objects.get(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        topic = utils.create_topic(category=category, user=self.user)
        form_data = {'user': self.user.username, }
        form = TopicPrivateInviteForm(data=form_data)
        form.topic = topic
        self.assertEqual(form.is_valid(), True)

    def test_private_join(self):
        """
        re-join private topic if user is the creator
        """
        private = utils.create_private_topic(user=self.user)
        private.delete()

        form_data = {}
        form = TopicPrivateJoinForm(user=self.user, topic=private.topic, data=form_data)
        self.assertTrue(form.is_valid())
        private_topic = form.save()
        self.assertEqual(private_topic.topic, private.topic)
        self.assertEqual(private_topic.user, private.user)

        # topic private exists
        private = utils.create_private_topic(user=self.user)
        form = TopicPrivateJoinForm(user=self.user, topic=private.topic, data=form_data)
        self.assertFalse(form.is_valid())


class TopicTemplateTagsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = Category.objects.get(pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK)
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_render_invite_form(self):
        """
        display invite form
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% render_invite_form topic %}"
        ).render(Context({'topic': self.topic, }))
        self.assertNotEqual(out, "")
        context = render_invite_form(self.topic)
        self.assertEqual(context['next'], None)
        self.assertIsInstance(context['form'], TopicPrivateInviteForm)
        self.assertEqual(context['topic'], self.topic)


class TopicPrivateUtilsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category)
        self.comment = utils.create_comment(topic=self.topic)

    def test_topic_private_notify_access(self):
        """
        Should create a notification
        """
        private = utils.create_private_topic()
        comment = utils.create_comment(topic=private.topic)
        notify_access(user=private.user, topic_private=private)
        notification = TopicNotification.objects.get(user=private.user, topic=private.topic)
        self.assertTrue(notification.is_active)
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.comment, comment)
