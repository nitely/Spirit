#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.test import TestCase, TransactionTestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

import utils

from spirit.models.topic_unread import TopicUnread, topic_viewed, comment_posted


class TopicUnreadViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
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
        response = self.client.get(reverse('spirit:topic-unread-list'))
        self.assertQuerysetEqual(response.context['page'], map(repr, [self.topic2, self.topic]))

        # fake next page
        response = self.client.get(reverse('spirit:topic-unread-list') + "?topic_id=" + str(self.topic2.pk))
        self.assertQuerysetEqual(response.context['page'], map(repr, [self.topic, ]))

    def test_topic_unread_list_show_private_topic(self):
        """
        topic private in unread list
        """
        TopicUnread.objects.all().delete()

        topic_a = utils.create_private_topic(user=self.user)
        TopicUnread.objects.create(user=self.user, topic=topic_a.topic, is_read=False)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic-unread-list'))
        self.assertQuerysetEqual(response.context['page'], map(repr, [topic_a.topic, ]))

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
        unread_a = TopicUnread.objects.create(user=self.user, topic=topic_a.topic, is_read=False)
        unread_b = TopicUnread.objects.create(user=self.user, topic=topic_b, is_read=False)
        unread_c = TopicUnread.objects.create(user=self.user, topic=topic_c, is_read=False)
        unread_d = TopicUnread.objects.create(user=self.user, topic=topic_d, is_read=False)
        unread_e = TopicUnread.objects.create(user=self.user, topic=topic_e, is_read=False)

        utils.login(self)
        response = self.client.get(reverse('spirit:topic-unread-list'))
        self.assertQuerysetEqual(response.context['page'], [])

    def test_topic_unread_list_invalid_topic_id(self):
        """
        invalid topic id
        """
        utils.login(self)
        last_pk = TopicUnread.objects.order_by("pk").last().pk
        response = self.client.get(reverse('spirit:topic-unread-list') + "?topic_id=" + str(last_pk + 1))
        self.assertEqual(response.status_code, 404)

    def test_topic_unread_list_empty_first_page(self):
        """
        empty first page
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:topic-unread-list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['page'], [])

    def test_topic_unread_list_empty_page(self):
        """
        empty page, other than the first one
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:topic-unread-list') + "?topic_id=" + str(self.topic.pk))
        self.assertEqual(response.status_code, 404)


class TopicUnreadSignalTest(TransactionTestCase):  # since signal raises IntegrityError

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.user2 = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(self.category)
        self.topic2 = utils.create_topic(self.category, user=self.user)

        self.topic_unread = TopicUnread.objects.create(user=self.user, topic=self.topic)
        self.topic_unread2 = TopicUnread.objects.create(user=self.user, topic=self.topic2)
        self.topic_unread3 = TopicUnread.objects.create(user=self.user2, topic=self.topic)

    def test_topic_unread_create_or_read_handler(self):
        """
        create or read when visiting topic
        """
        req = RequestFactory().get('/')
        req.user = self.user
        TopicUnread.objects.all().update(is_read=False)
        topic_viewed.send(sender=self.topic.__class__, request=req, topic=self.topic)
        self.assertTrue(TopicUnread.objects.get(user=self.user, topic=self.topic).is_read)

        req.user = self.user2
        topic_viewed.send(sender=self.topic.__class__, request=req, topic=self.topic)
        self.assertEqual(len(TopicUnread.objects.filter(user=self.user2, topic=self.topic)), 1)
        self.assertTrue(TopicUnread.objects.get(user=self.user2, topic=self.topic).is_read)

    def test_topic_unread_bulk_handler(self):
        """
        mark as unread when comment posted
        """
        TopicUnread.objects.all().update(is_read=True)
        comment = utils.create_comment(user=self.user, topic=self.topic)
        comment_posted.send(sender=self.topic.__class__, comment=comment, mentions=None)
        self.assertTrue(TopicUnread.objects.get(user=self.user, topic=self.topic).is_read)
        self.assertFalse(TopicUnread.objects.get(user=self.user2, topic=self.topic).is_read)