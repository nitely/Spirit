# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ...core.tests import utils
from ...comment.models import Comment, CLOSED, UNCLOSED, PINNED, UNPINNED
from ..models import Topic


class TopicViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()

    def test_topic_moderate_delete(self):
        """
        delete topic
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        yesterday = timezone.now() - datetime.timedelta(days=1)
        category = utils.create_category()
        topic = utils.create_topic(category, reindex_at=yesterday)
        self.assertEqual(topic.reindex_at, yesterday)
        response = self.client.post(
            reverse('spirit:topic:moderate:delete', kwargs={'pk': topic.pk}),
            data={})
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

        topic = Topic.objects.get(pk=topic.pk)
        self.assertTrue(topic.is_removed)
        self.assertGreater(topic.reindex_at, yesterday)

    def test_topic_moderate_undelete(self):
        """
        undelete topic
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        yesterday = timezone.now() - datetime.timedelta(days=1)
        category = utils.create_category()
        topic = utils.create_topic(category, is_removed=True, reindex_at=yesterday)
        self.assertEqual(topic.reindex_at, yesterday)
        response = self.client.post(
            reverse('spirit:topic:moderate:undelete', kwargs={'pk': topic.pk}),
            data={})
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)

        topic = Topic.objects.get(pk=topic.pk)
        self.assertFalse(topic.is_removed)
        self.assertGreater(topic.reindex_at, yesterday)

    def test_topic_moderate_lock(self):
        """
        topic lock
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(
            reverse('spirit:topic:moderate:lock', kwargs={'pk': topic.pk, }),
            form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_closed)
        self.assertEqual(
            len(Comment.objects.filter(user=self.user, topic=topic, action=CLOSED)),
            1)

    def test_topic_moderate_unlock(self):
        """
        unlock topic
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_closed=True)
        form_data = {}
        response = self.client.post(
            reverse('spirit:topic:moderate:unlock', kwargs={'pk': topic.pk, }),
            form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_closed)
        self.assertEqual(
            len(Comment.objects.filter(user=self.user, topic=topic, action=UNCLOSED)),
            1)

    def test_topic_moderate_pin(self):
        """
        topic pin
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(
            reverse('spirit:topic:moderate:pin', kwargs={'pk': topic.pk, }),
            form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_pinned)
        self.assertEqual(
            len(Comment.objects.filter(user=self.user, topic=topic, action=PINNED)),
            1)

    def test_topic_moderate_unpin(self):
        """
        topic unpin
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_pinned=True)
        form_data = {}
        response = self.client.post(
            reverse('spirit:topic:moderate:unpin', kwargs={'pk': topic.pk, }),
            form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_pinned)
        self.assertEqual(
            len(Comment.objects.filter(user=self.user, topic=topic, action=UNPINNED)),
            1)

    def test_topic_moderate_global_pin(self):
        """
        topic pin
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(
            reverse('spirit:topic:moderate:global-pin', kwargs={'pk': topic.pk, }),
            form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_globally_pinned)
        self.assertEqual(
            len(Comment.objects.filter(user=self.user, topic=topic, action=PINNED)),
            1)

    def test_topic_moderate_global_unpin(self):
        """
        topic unpin
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_globally_pinned=True)
        form_data = {}
        response = self.client.post(
            reverse('spirit:topic:moderate:global-unpin', kwargs={'pk': topic.pk, }),
            form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_globally_pinned)
        self.assertEqual(
            len(Comment.objects.filter(user=self.user, topic=topic, action=UNPINNED)),
            1)
