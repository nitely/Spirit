#-*- coding: utf-8 -*-

import datetime

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.utils import timezone

import utils

from spirit.models.topic import Topic


class CategoryViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()
        self.category_1 = utils.create_category(title="cat1")
        self.subcategory_1 = utils.create_subcategory(self.category_1)
        self.category_2 = utils.create_category(title="cat2")
        self.category_removed = utils.create_category(title="cat3", is_removed=True)

    def test_category_list_view(self):
        """
        should display all categories
        """
        response = self.client.get(reverse('spirit:category-list'))
        self.assertQuerysetEqual(response.context['categories'], ['<Category: Uncategorized>', repr(self.category_1), repr(self.category_2)])

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
        topic_c = utils.create_topic(category=self.category_1, is_pinned=True, is_removed=True)
        # show pinned first
        Topic.objects.filter(pk=topic_a.pk).update(last_active=timezone.now() - datetime.timedelta(days=10))

        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': self.category_1.pk,
                                                                             'slug': self.category_1.slug}))
        self.assertQuerysetEqual(response.context['topics'], map(repr, [topic_a, topic_b, ]))

    def test_category_detail_view_removed_topics(self):
        """
        should not display removed topics or from other categories
        """
        subcategory_removed = utils.create_subcategory(self.category_1, is_removed=True)
        topic_removed = utils.create_topic(category=subcategory_removed)
        topic_removed2 = utils.create_topic(category=self.category_1, is_removed=True)
        topic_bad = utils.create_topic(category=self.category_2)

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
        topic = utils.create_topic(category=self.category_1)
        topic2 = utils.create_topic(category=self.subcategory_1, title="topic_subcat1")
        response = self.client.get(reverse('spirit:category-detail', kwargs={'pk': self.subcategory_1.pk,
                                                                             'slug': self.subcategory_1.slug}))
        self.assertQuerysetEqual(response.context['topics'], [repr(topic2), ])
        self.assertQuerysetEqual(response.context['categories'], [])