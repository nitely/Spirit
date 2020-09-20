# -*- coding: utf-8 -*-

import datetime
import importlib

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.apps import apps

from djconfig.utils import override_djconfig

from ..core.conf import settings
from ..core.tests import utils
from ..topic.models import Topic
from ..comment.bookmark.models import CommentBookmark
from .models import Category

data_migration_0006 = importlib.import_module(
    'spirit.category.migrations.0006_auto_20190120_0406')


class CategoryViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category_1 = utils.create_category(title="cat1")
        self.subcategory_1 = utils.create_subcategory(self.category_1)
        self.category_2 = utils.create_category(title="cat2")
        self.category_removed = utils.create_category(
            title="cat3", is_removed=True)

    def test_category_detail_view(self):
        """
        should display all topics in the category and its subcategories
        ordered by last active first
        """
        topic = utils.create_topic(category=self.category_1)
        topic2 = utils.create_topic(category=self.subcategory_1)
        topic3 = utils.create_topic(category=self.category_1)

        (Topic.objects
         .filter(pk=topic.pk)
         .update(last_active=timezone.now() - datetime.timedelta(days=10)))
        (Topic.objects
         .filter(pk=topic3.pk)
         .update(last_active=timezone.now() - datetime.timedelta(days=5)))

        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': self.category_1.pk, 'slug': self.category_1.slug}))
        self.assertEqual(
            list(response.context['topics']), [topic2, topic3, topic])

    def test_category_detail_view_order(self):
        """
        should display all topics order by pinned and last active
        """
        topic_a = utils.create_topic(category=self.category_1, is_pinned=True)
        topic_b = utils.create_topic(category=self.category_1)
        utils.create_topic(
            category=self.category_1, is_pinned=True, is_removed=True)
        # show pinned first
        (Topic.objects
         .filter(pk=topic_a.pk)
         .update(last_active=timezone.now() - datetime.timedelta(days=10)))

        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': self.category_1.pk, 'slug': self.category_1.slug}))
        self.assertEqual(list(response.context['topics']), [topic_a, topic_b])

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
        (Topic.objects
         .filter(pk=topic_d.pk)
         .update(last_active=timezone.now() - datetime.timedelta(days=10)))

        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': category.pk, 'slug': category.slug}))
        self.assertEqual(
            list(response.context['topics']),
            [topic_d, topic_b, topic_c, topic_a])

    def test_category_detail_view_removed_topics(self):
        """
        should not display removed topics or from other categories
        """
        subcategory_removed = utils.create_subcategory(
            self.category_1, is_removed=True)
        utils.create_topic(category=subcategory_removed)
        utils.create_topic(category=self.category_1, is_removed=True)
        utils.create_topic(category=self.category_2)

        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': self.category_1.pk, 'slug': self.category_1.slug}))
        self.assertEqual(list(response.context['topics']), [])

    def test_category_detail_view_invalid_category(self):
        """
        invalid category
        """
        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={'pk': str(99)}))
        self.assertEqual(response.status_code, 404)

    def test_category_detail_view_invalid_slug(self):
        """
        invalid slug
        """
        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': self.category_1.pk, 'slug': 'bar'}))
        self.assertRedirects(
            response, self.category_1.get_absolute_url(), status_code=301)

    def test_category_detail_view_no_slug(self):
        """
        no slug
        """
        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': self.category_1.pk, 'slug': ''}))
        self.assertRedirects(
            response, self.category_1.get_absolute_url(), status_code=301)

    def test_category_detail_subcategory(self):
        """
        should display all topics in  subcategory
        """
        utils.create_topic(category=self.category_1)
        topic2 = utils.create_topic(
            category=self.subcategory_1, title="topic_subcat1")
        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': self.subcategory_1.pk, 'slug': self.subcategory_1.slug}))
        self.assertEqual(list(response.context['topics']), [topic2])
        self.assertEqual(list(response.context['categories']), [])

    def test_category_detail_view_bookmarks(self):
        """
        topics should have bookmarks
        """
        utils.login(self)
        topic = utils.create_topic(category=self.category_1)
        bookmark = CommentBookmark.objects.create(topic=topic, user=self.user)

        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': self.category_1.pk, 'slug': self.category_1.slug}))
        self.assertEqual(list(response.context['topics']), [topic])
        self.assertEqual(response.context['topics'][0].bookmark, bookmark)

    @override_djconfig(topics_per_page=1)
    def test_category_detail_view_paginate(self):
        """
        List of topics paginated
        """
        utils.create_topic(category=self.category_1)
        topic = utils.create_topic(category=self.category_1)

        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': self.category_1.pk, 'slug': self.category_1.slug}))
        self.assertEqual(list(response.context['topics']), [topic])

    @override_settings(ST_ORDERED_CATEGORIES=True)
    def test_detail_subcategories_ordered(self):
        Category.objects.all().delete()
        cat_parent = utils.create_category()
        cat1 = utils.create_category(title="1", sort=2, parent=cat_parent)
        cat2 = utils.create_category(title="2", sort=1, parent=cat_parent)
        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': cat_parent.pk, 'slug': cat_parent.slug}))
        self.assertEqual(
            list(response.context['subcategories']), [cat2, cat1])
        cat1.sort = 0
        cat1.save()
        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': cat_parent.pk, 'slug': cat_parent.slug}))
        self.assertEqual(
            list(response.context['subcategories']), [cat1, cat2])

    @override_settings(ST_ORDERED_CATEGORIES=False)
    def test_detail_subcategories_title_order(self):
        Category.objects.all().delete()
        cat_parent = utils.create_category()
        cat1 = utils.create_category(title="1", sort=2, parent=cat_parent)
        cat2 = utils.create_category(title="2", sort=1, parent=cat_parent)
        response = self.client.get(reverse(
            'spirit:category:detail', kwargs={
                'pk': cat_parent.pk, 'slug': cat_parent.slug}))
        self.assertEqual(
            list(response.context['subcategories']), [cat1, cat2])


class CategoryModelTest(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_is_subcategory(self):
        """
        Should return whether the category\
        is a subcategory or not
        """
        category = utils.create_category()
        subcategory = utils.create_category(parent=category)
        self.assertEqual(category.is_subcategory, False)
        self.assertEqual(subcategory.is_subcategory, True)

    def test_reindex_at(self):
        """
        Should not always update reindex_at
        """
        category = utils.create_category()
        reindex_at = category.reindex_at
        category.save()  # No changes
        self.assertEqual(
            reindex_at,
            Category.objects.get(pk=category.pk).reindex_at)


class CategoryMigrationTest(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_uncategorized_category(self):
        """
        There should be a category named Uncategorized
        """
        self.assertEqual(
            len(Category.objects.filter(title="Uncategorized")), 1)

    def test_private_category(self):
        """
        There should be a private category
        """
        self.assertEqual(len(Category.objects.filter(
            pk=settings.ST_TOPIC_PRIVATE_CATEGORY_PK,
            title="Private")), 1)

    def test_categories(self):
        """
        There should be two categories: private and Uncategorized
        """
        self.assertEqual(len(Category.objects.all()), 2)

    def test_migration_0006(self):
        utils.create_category(sort=0)
        utils.create_category(sort=0)
        utils.create_category(sort=0)
        data_migration_0006.reorder(apps, None)
        last = 0
        for category in Category.objects.all():
            self.assertTrue(category.sort > last)
            last = category.sort
