# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse

from ...core.tests import utils
from .models import TopicUnread
from ...comment.bookmark.models import CommentBookmark


class TopicUnreadViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category)
        self.topic2 = utils.create_topic(self.category, user=self.user)
        self.topic3 = utils.create_topic(self.category, user=self.user)
        self.topic4 = utils.create_topic(self.category, user=self.user)

        self.topic_unread = TopicUnread.objects.create(user=self.user, topic=self.topic)
        self.topic_unread2 = TopicUnread.objects.create(user=self.user, topic=self.topic2)
        self.topic_unread4 = TopicUnread.objects.create(user=self.user, topic=self.topic4)
        self.topic_unread5 = TopicUnread.objects.create(user=self.user2, topic=self.topic)

    def test_topic_unread_list(self):
        """
        topic unread list
        """
        TopicUnread.objects.filter(pk__in=[self.topic_unread.pk, self.topic_unread2.pk])\
            .update(is_read=False)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:unread:index'))
        self.assertEqual(list(response.context['page']), [self.topic2, self.topic])

        # fake next page
        response = self.client.get(reverse('spirit:topic:unread:index') + "?topic_id=" + str(self.topic2.pk))
        self.assertEqual(list(response.context['page']), [self.topic, ])

    def test_topic_unread_list_show_private_topic(self):
        """
        topic private in unread list
        """
        TopicUnread.objects.all().delete()

        topic_a = utils.create_private_topic(user=self.user)
        TopicUnread.objects.create(user=self.user, topic=topic_a.topic, is_read=False)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:unread:index'))
        self.assertEqual(list(response.context['page']), [topic_a.topic, ])

    def test_topic_unread_list_dont_show_removed_or_no_access(self):
        """
        dont show private topics if user has no access or is removed
        """
        TopicUnread.objects.all().delete()

        category = utils.create_category()
        category_removed = utils.create_category(is_removed=True)
        subcategory = utils.create_category(parent=category_removed)
        subcategory_removed = utils.create_category(parent=category, is_removed=True)
        topic_a = utils.create_private_topic()
        topic_b = utils.create_topic(category=category, is_removed=True)
        topic_c = utils.create_topic(category=category_removed)
        topic_d = utils.create_topic(category=subcategory)
        topic_e = utils.create_topic(category=subcategory_removed)
        TopicUnread.objects.create(user=self.user, topic=topic_a.topic, is_read=False)
        TopicUnread.objects.create(user=self.user, topic=topic_b, is_read=False)
        TopicUnread.objects.create(user=self.user, topic=topic_c, is_read=False)
        TopicUnread.objects.create(user=self.user, topic=topic_d, is_read=False)
        TopicUnread.objects.create(user=self.user, topic=topic_e, is_read=False)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:unread:index'))
        self.assertEqual(list(response.context['page']), [])

    def test_topic_unread_list_invalid_topic_id(self):
        """
        invalid topic id
        """
        utils.login(self)
        last_pk = TopicUnread.objects.order_by("pk").last().pk
        response = self.client.get(reverse('spirit:topic:unread:index') + "?topic_id=" + str(last_pk + 1))
        self.assertEqual(response.status_code, 404)

    def test_topic_unread_list_empty_first_page(self):
        """
        empty first page
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:topic:unread:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['page']), [])

    def test_topic_unread_list_empty_page(self):
        """
        empty page, other than the first one
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:topic:unread:index') + "?topic_id=" + str(self.topic.pk))
        self.assertEqual(response.status_code, 404)

    def test_topic_unread_list_bookmarks(self):
        """
        topic unread list with bookmarks
        """
        TopicUnread.objects\
            .filter(pk__in=[self.topic_unread.pk, self.topic_unread2.pk])\
            .update(is_read=False)
        bookmark = CommentBookmark.objects.create(topic=self.topic2, user=self.user)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic:unread:index'))
        self.assertEqual(list(response.context['page']), [self.topic2, self.topic])
        self.assertEqual(response.context['page'][0].bookmark, bookmark)


class TopicUnreadModelsTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category)
        self.topic2 = utils.create_topic(self.category, user=self.user)

        self.topic_unread = TopicUnread.objects.create(user=self.user, topic=self.topic)
        self.topic_unread2 = TopicUnread.objects.create(user=self.user, topic=self.topic2)
        self.topic_unread3 = TopicUnread.objects.create(user=self.user2, topic=self.topic)

    def test_topic_unread_create_or_mark_as_read(self):
        """
        create or mark as read
        """
        user = utils.create_user()
        TopicUnread.create_or_mark_as_read(user=user, topic=self.topic)
        self.assertEqual(len(TopicUnread.objects.filter(user=user, topic=self.topic)), 1)

        TopicUnread.objects.all().update(is_read=True)
        TopicUnread.create_or_mark_as_read(user=user, topic=self.topic)
        self.assertTrue(TopicUnread.objects.get(user=user, topic=self.topic).is_read)

    def test_topic_unread_new_comment(self):
        """
        Mark as unread
        """
        TopicUnread.objects.all().update(is_read=True)
        comment = utils.create_comment(user=self.user, topic=self.topic)
        TopicUnread.unread_new_comment(comment=comment)
        self.assertTrue(TopicUnread.objects.get(user=self.user, topic=self.topic).is_read)
        self.assertFalse(TopicUnread.objects.get(user=self.user2, topic=self.topic).is_read)
