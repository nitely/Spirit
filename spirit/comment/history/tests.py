# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse

from djconfig.utils import override_djconfig

from ...core.tests import utils
from .models import CommentHistory
from . import models


class CommentHistoryViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_comment_history_detail(self):
        """
        history comment
        """
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment_history = CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)
        comment2 = utils.create_comment(user=self.user, topic=self.topic)
        CommentHistory.objects.create(comment_fk=comment2, comment_html=comment2.comment_html)

        utils.login(self)
        response = self.client.get(reverse('spirit:comment:history:detail', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(list(response.context['comments']), [comment_history, ])

    @override_djconfig(comments_per_page=1)
    def test_comment_history_detail_paginate(self):
        """
        history comment paginate
        """
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment_history = CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)

        utils.login(self)
        response = self.client.get(reverse('spirit:comment:history:detail', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(list(response.context['comments']), [comment_history, ])

    def test_comment_history_detail_private_topic(self):
        """
        history should work for private topics
        """
        private = utils.create_private_topic(user=self.user)
        comment = utils.create_comment(user=self.user, topic=private.topic)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)

        utils.login(self)
        response = self.client.get(reverse('spirit:comment:history:detail', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 200)

    def test_comment_history_detail_removed(self):
        """
        return Http404 if comment is removed
        """
        utils.login(self)

        # comment removed
        comment = utils.create_comment(user=self.user, topic=self.topic, is_removed=True)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)
        response = self.client.get(reverse('spirit:comment:history:detail', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 404)

        # topic removed
        topic = utils.create_topic(category=self.category, user=self.user, is_removed=True)
        comment = utils.create_comment(user=self.user, topic=topic)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)
        response = self.client.get(reverse('spirit:comment:history:detail', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 404)

        # category removed
        category = utils.create_category(is_removed=True)
        topic = utils.create_topic(category=category, user=self.user)
        comment = utils.create_comment(user=self.user, topic=topic)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)
        response = self.client.get(reverse('spirit:comment:history:detail', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 404)

    def test_comment_history_detail_no_access(self):
        """
        return Http404 if user has no access to the comment's topic
        """
        private = utils.create_private_topic(user=self.user)
        private.delete()

        comment = utils.create_comment(user=self.user, topic=private.topic)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)

        utils.login(self)
        response = self.client.get(reverse('spirit:comment:history:detail', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 404)

    def test_comment_history_detail_denied_to_non_logged_users(self):
        """
        history should not be seen by guests
        """
        comment = utils.create_comment(user=self.user, topic=self.topic)
        response = self.client.get(reverse('spirit:comment:history:detail', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 302)


class CommentHistoryModelsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_comment_history_create_maybe(self):
        """
        should create the comment (hystory) if a comment for it does not exists
        """
        comment = utils.create_comment(topic=self.topic)
        comment_history = CommentHistory.create_maybe(comment)
        self.assertTrue(comment_history.pk)
        comment_history2 = CommentHistory.create_maybe(comment)
        self.assertIsNone(comment_history2)
        self.assertEqual(len(CommentHistory.objects.filter(comment_fk=comment.pk)), 1)

    def test_comment_history_create_maybe_date(self):
        """
        should create the comment (hystory) with the original comment date
        """
        yesterday = models.timezone.now() - timedelta(1)
        comment = utils.create_comment(topic=self.topic, date=yesterday)
        comment_history = CommentHistory.create_maybe(comment)
        self.assertIsNotNone(comment_history)
        self.assertEqual(comment_history.date, comment.date)

    def test_comment_history_create(self):
        yesterday = models.timezone.now() - timedelta(1)
        comment = utils.create_comment(topic=self.topic, date=yesterday)
        comment_history = CommentHistory.create(comment)
        self.assertTrue(comment_history.pk)
        self.assertEqual(comment_history.comment_fk, comment)
        self.assertEqual(comment_history.comment_html, comment.comment_html)
        self.assertNotEqual(comment_history.date, yesterday)

    def test_comment_history_create_date(self):
        now = models.timezone.now()
        yesterday = now - timedelta(1)

        class MockTZ:
            @classmethod
            def now(cls):
                return now

        org_tz, models.timezone = models.timezone, MockTZ
        try:
            comment = utils.create_comment(topic=self.topic, date=yesterday)
            comment_history = CommentHistory.create(comment)
            self.assertTrue(comment_history.pk)
            self.assertEqual(comment_history.date, now)
        finally:
            models.timezone = org_tz
