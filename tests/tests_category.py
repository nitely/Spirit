# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.utils import timezone

from djconfig.utils import override_djconfig

from . import utils

from spirit.models.topic import Topic
from spirit.models.comment_bookmark import CommentBookmark


class CategoryViewTest(TestCase):

    def setUp(self):
        cache.clear()
        self.user = utils.create_user()
        self.category_1 = utils.create_category(title="cat1")
        self.subcategory_1 = utils.create_subcategory(self.category_1)
        self.category_2 = utils.create_category(title="cat2")
        self.category_removed = utils.create_category(title="cat3", is_removed=True)

    def test_category_list_view(self):
        """
        should display all categories
        """
        response = self.client.get(reverse('spirit:category-list'))
        self.assertQuerysetEqual(
            response.context['categories'],
            ['<Category: Uncategorized>', repr(self.category_1), repr(self.category_2)]
        )

    def test_category_detail_view(self):
        """
        should display all topics in the category and its subcategories
        ordered by last active first
        """
        topic = utils.create_topic(category=self.category_1)
        topic2 = utils.create_topic(category=self.subcategory_1)
        topic3 = utils.create_topic(category=self.category_1)

        Topic.objects.filter(pk=topic.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))
        Topic.objects.filter(pk=topic3.pk).update(last_active=timezone.now() - datetime.timedelta(days=5))

        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': self.category_1.pk,
                                                                             'slug': self.category_1.slug}))
        self.assertQuerysetEqual(response.context['topics'], [repr(topic2), repr(topic3), repr(topic)])

    def test_category_detail_view_order(self):
        """
        should display all topics order by pinned and last active
        """
        topic_a = utils.create_topic(category=self.category_1, is_pinned=True)
        topic_b = utils.create_topic(category=self.category_1)
        utils.create_topic(category=self.category_1, is_pinned=True, is_removed=True)
        # show pinned first
        Topic.objects.filter(pk=topic_a.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))

        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': self.category_1.pk,
                                                                             'slug': self.category_1.slug}))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_a, topic_b, ]))

    def test_category_detail_view_pinned(self):
        """
        Show globally pinned topics first, then regular pinned topics, then regular topics
        """
        category = utils.create_category()
        topic_a = utils.create_topic(category=category)
        topic_b = utils.create_topic(category=category, is_pinned=True)
        topic_c = utils.create_topic(category=category)
        topic_d = utils.create_topic(category=category, is_globally_pinned=True)
        # show globally pinned first
        Topic.objects.filter(pk=topic_d.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))

        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': category.pk,
                                                                             'slug': category.slug}))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_d, topic_b, topic_c, topic_a]))

    def test_category_detail_view_removed_topics(self):
        """
        should not display removed topics or from other categories
        """
        subcategory_removed = utils.create_subcategory(self.category_1, is_removed=True)
        utils.create_topic(category=subcategory_removed)
        utils.create_topic(category=self.category_1, is_removed=True)
        utils.create_topic(category=self.category_2)

        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': self.category_1.pk,
                                                                             'slug': self.category_1.slug}))
        self.assertQuerysetEqual(response.context['topics'], [])

    def test_category_detail_view_invalid_category(self):
        """
        invalid category
        """
        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': str(99), }))
        self.assertEqual(response.status_code, 404)

    def test_category_detail_view_invalid_slug(self):
        """
        invalid slug
        """
        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': self.category_1.pk,
                                                                             'slug': 'bar'}))
        self.assertRedirects(response, self.category_1.get_absolute_url(), status_code=301)

    def test_category_detail_view_no_slug(self):
        """
        no slug
        """
        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': self.category_1.pk,
                                                                             'slug': ''}))
        self.assertRedirects(response, self.category_1.get_absolute_url(), status_code=301)

    def test_category_detail_subcategory(self):
        """
        should display all topics in  subcategory
        """
        utils.create_topic(category=self.category_1)
        topic2 = utils.create_topic(category=self.subcategory_1, title="topic_subcat1")
        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': self.subcategory_1.pk,
                                                                             'slug': self.subcategory_1.slug}))
        self.assertQuerysetEqual(response.context['topics'], [repr(topic2), ])
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_category_detail_view_bookmarks(self):
        """
        topics should have bookmarks
        """
        utils.login(self)
        topic = utils.create_topic(category=self.category_1)
        bookmark = CommentBookmark.objects.create(topic=topic, user=self.user)

        response = self.client.get(reverse('spirit:category-detail',
                                           kwargs={'pk': self.category_1.pk,
                                                   'slug': self.category_1.slug}))
        self.assertQuerysetEqual(response.context['topics'], [repr(topic), ])
        self.assertEqual(response.context['topics'][0].bookmark, bookmark)

    @override_djconfig(topics_per_page=1)
    def test_category_detail_view_paginate(self):
        """
        List of topics paginated
        """
        utils.create_topic(category=self.category_1)
        topic = utils.create_topic(category=self.category_1)

        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': self.category_1.pk,
                                                                             'slug': self.category_1.slug}))
        self.assertQuerysetEqual(response.context['topics'], [repr(topic), ])
