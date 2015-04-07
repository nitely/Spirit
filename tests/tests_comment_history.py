# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.cache import cache
from djconfig.utils import override_djconfig

from . import utils
from spirit.apps.comment.history.models import CommentHistory
from spirit.apps.comment.signals import comment_pre_update, comment_post_update


class CommentHistoryViewTest(TestCase):

    def setUp(self):
        cache.clear()
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
        response = self.client.get(reverse('spirit:comment-history', kwargs={'comment_id': comment.pk, }))
        self.assertQuerysetEqual(response.context['comments'], map(repr, [comment_history, ]))

    @override_djconfig(comments_per_page=1)
    def test_comment_history_detail_paginate(self):
        """
        history comment paginate
        """
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment_history = CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)

        utils.login(self)
        response = self.client.get(reverse('spirit:comment-history', kwargs={'comment_id': comment.pk, }))
        self.assertQuerysetEqual(response.context['comments'], map(repr, [comment_history, ]))

    def test_comment_history_detail_private_topic(self):
        """
        history should work for private topics
        """
        private = utils.create_private_topic(user=self.user)
        comment = utils.create_comment(user=self.user, topic=private.topic)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)

        utils.login(self)
        response = self.client.get(reverse('spirit:comment-history', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 200)

    def test_comment_history_detail_removed(self):
        """
        return Http404 if comment is removed
        """
        utils.login(self)

        # comment removed
        comment = utils.create_comment(user=self.user, topic=self.topic, is_removed=True)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)
        response = self.client.get(reverse('spirit:comment-history', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 404)

        # topic removed
        topic = utils.create_topic(category=self.category, user=self.user, is_removed=True)
        comment = utils.create_comment(user=self.user, topic=topic)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)
        response = self.client.get(reverse('spirit:comment-history', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 404)

        # category removed
        category = utils.create_category(is_removed=True)
        topic = utils.create_topic(category=category, user=self.user)
        comment = utils.create_comment(user=self.user, topic=topic)
        CommentHistory.objects.create(comment_fk=comment, comment_html=comment.comment_html)
        response = self.client.get(reverse('spirit:comment-history', kwargs={'comment_id': comment.pk, }))
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
        response = self.client.get(reverse('spirit:comment-history', kwargs={'comment_id': comment.pk, }))
        self.assertEqual(response.status_code, 404)


class CommentHistorySignalTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user)

    def test_comment_history_comment_pre_update_handler(self):
        """
        comment_pre_update_handler signal
        """
        comment = utils.create_comment(topic=self.topic)
        comment_pre_update.send(sender=comment.__class__, comment=comment)
        self.assertEqual(CommentHistory.objects.get(comment_fk=comment.pk).comment_html, comment.comment_html)
        self.assertEqual(len(CommentHistory.objects.filter(comment_fk=comment.pk)), 1)
        comment_pre_update.send(sender=comment.__class__, comment=comment)
        self.assertEqual(len(CommentHistory.objects.filter(comment_fk=comment.pk)), 1)

    def test_comment_history_comment_post_update_handler(self):
        comment = utils.create_comment(topic=self.topic)
        comment_post_update.send(sender=comment.__class__, comment=comment)
        self.assertEqual(CommentHistory.objects.get(comment_fk=comment.pk).comment_html, comment.comment_html)
        comment_post_update.send(sender=comment.__class__, comment=comment)
        self.assertEqual(len(CommentHistory.objects.filter(comment_fk=comment.pk)), 2)
