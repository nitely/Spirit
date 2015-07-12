# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.cache import cache
from django.core.urlresolvers import reverse

from ...core.tests import utils
from ...comment.models import CLOSED, UNCLOSED, PINNED, UNPINNED
from ..models import Topic
from .signals import topic_post_moderate


class TopicViewTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()

    def test_topic_moderate_delete(self):
        """
        delete topic
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:moderate:delete', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_removed)

    def test_topic_moderate_undelete(self):
        """
        undelete topic
        """
        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_removed=True)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:moderate:undelete', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_removed)

    def test_topic_moderate_lock(self):
        """
        topic lock
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:moderate:lock', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_closed)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), CLOSED])

    def test_topic_moderate_unlock(self):
        """
        unlock topic
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_closed=True)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:moderate:unlock', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_closed)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), UNCLOSED])

    def test_topic_moderate_pin(self):
        """
        topic pin
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:moderate:pin', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_pinned)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), PINNED])

    def test_topic_moderate_unpin(self):
        """
        topic unpin
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_pinned=True)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:moderate:unpin', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_pinned)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), UNPINNED])

    def test_topic_moderate_global_pin(self):
        """
        topic pin
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:moderate:global-pin', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertTrue(Topic.objects.get(pk=topic.pk).is_globally_pinned)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), PINNED])

    def test_topic_moderate_global_unpin(self):
        """
        topic unpin
        """
        def topic_post_moderate_handler(sender, user, topic, action, **kwargs):
            self._moderate = [repr(user._wrapped), repr(topic), action]
        topic_post_moderate.connect(topic_post_moderate_handler)

        utils.login(self)
        self.user.st.is_moderator = True
        self.user.save()

        category = utils.create_category()
        topic = utils.create_topic(category, is_globally_pinned=True)
        form_data = {}
        response = self.client.post(reverse('spirit:topic:moderate:global-unpin', kwargs={'pk': topic.pk, }),
                                    form_data)
        expected_url = topic.get_absolute_url()
        self.assertRedirects(response, expected_url, status_code=302)
        self.assertFalse(Topic.objects.get(pk=topic.pk).is_globally_pinned)
        self.assertEqual(self._moderate, [repr(self.user), repr(topic), UNPINNED])
