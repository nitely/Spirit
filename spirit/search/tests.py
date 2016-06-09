# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.conf import settings
from django.core.management import call_command

from haystack.query import SearchQuerySet
from djconfig.utils import override_djconfig

from ..core.tests import utils
from ..topic.models import Topic
from .forms import BasicSearchForm, AdvancedSearchForm
from .tags import render_search_form
from .search_indexes import TopicIndex

HAYSTACK_TEST = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine'}}


def rebuild_index():
    call_command("rebuild_index", verbosity=0, interactive=False)


class SearchTopicIndexTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.topic_sqs = SearchQuerySet().models(Topic)

    def test_index_queryset_excludes_private_topics(self):
        """
        index_queryset should exclude private topics
        """
        utils.create_private_topic()
        self.assertEqual(len(TopicIndex().index_queryset()), 0)

        category = utils.create_category()
        utils.create_topic(category)
        self.assertEqual(len(TopicIndex().index_queryset()), 1)

    def test_indexing_excludes_private_topics(self):
        """
        rebuild_index command should exclude private topics
        """
        utils.create_private_topic()
        category = utils.create_category()
        topic = utils.create_topic(category)
        rebuild_index()

        self.assertEqual([s.object for s in self.topic_sqs], [topic])

    def test_indexing_is_removed(self):
        """
        Should set the removed flag when either\
        topic, subcategory or category are removed
        """
        main_category = utils.create_category()
        category = utils.create_category(parent=main_category)
        topic = utils.create_topic(category)

        rebuild_index()
        self.assertEqual(
            len(self.topic_sqs.filter(is_removed=False)), 1)

        topic.is_removed = True
        topic.save()
        rebuild_index()
        self.assertEqual(
            len(self.topic_sqs.filter(is_removed=False)), 0)

        category.is_removed = True
        category.save()
        topic.is_removed = False
        topic.save()
        rebuild_index()
        self.assertEqual(
            len(self.topic_sqs.filter(is_removed=False)), 0)

        main_category.is_removed = True
        main_category.save()
        category.is_removed = False
        category.save()
        topic.is_removed = False
        topic.save()
        rebuild_index()
        self.assertEqual(
            len(self.topic_sqs.filter(is_removed=False)), 0)

        main_category.is_removed = False
        main_category.save()
        rebuild_index()
        self.assertEqual(
            len(self.topic_sqs.filter(is_removed=False)), 1)

    def test_indexing_slug_empty(self):
        """
        Should store the slug as an empty string
        """
        category = utils.create_category()
        topic = utils.create_topic(category)
        topic.slug = ''
        topic.save()
        rebuild_index()
        self.assertEqual(len(self.topic_sqs.all()), 1)
        self.assertEqual(
            list(self.topic_sqs.all())[0]
            .get_stored_fields()['slug'],
            '')

    def test_indexing_main_category_name(self):
        """
        Should store the main category name
        """
        main_category = utils.create_category()
        category = utils.create_category(parent=main_category)
        utils.create_topic(category)
        rebuild_index()
        self.assertEqual(len(self.topic_sqs.all()), 1)
        self.assertEqual(
            list(self.topic_sqs.all())[0]
            .get_stored_fields()['main_category_name'],
            main_category.title)


class SearchViewTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(
            category=self.category, user=self.user, title="spirit search test foo")
        self.topic2 = utils.create_topic(
            category=self.category, user=self.user, title="foo")

        rebuild_index()

    def test_search_requires_login(self):
        """
        Should require to be logged-in
        """
        response = self.client.get(reverse('spirit:search:search'))
        self.assertEqual(response.status_code, 302)

        utils.login(self)
        response = self.client.get(reverse('spirit:search:search'))
        self.assertEqual(response.status_code, 200)

    def test_advanced_search_detail(self):
        """
        advanced search by topic
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:search:search'))
        self.assertEqual(response.status_code, 200)

    def test_advanced_search_topics(self):
        """
        advanced search by topic
        """
        utils.login(self)
        data = {'q': 'spirit search'}
        response = self.client.get(
            reverse('spirit:search:search'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['page']),
            [{
                'fields': {
                    'title': self.topic.title,
                    'slug': self.topic.slug,
                    'comment_count': self.topic.comment_count,
                    'last_active': self.topic.last_active,
                    'main_category_name': self.topic.main_category.title},
                'pk': str(self.topic.pk)}])

    @override_djconfig(topics_per_page=1)
    def test_advanced_search_topics_paginate(self):
        """
        advanced search by topic paginated
        """
        utils.login(self)
        data = {'q': 'foo', }
        response = self.client.get(
            reverse('spirit:search:search'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['page']),
            [{
                'fields': {
                    'title': self.topic2.title,
                    'slug': self.topic2.slug,
                    'comment_count': self.topic2.comment_count,
                    'last_active': self.topic2.last_active,
                    'main_category_name': self.topic2.main_category.title},
                'pk': str(self.topic2.pk)}])

    def test_advanced_search_in_category(self):
        """
        search by topic in category
        """
        utils.login(self)
        category = utils.create_category()
        data = {'q': 'spirit search', 'category': category.pk}
        response = self.client.get(reverse('spirit:search:search'),
                                   data)
        self.assertEqual(list(response.context['page']), [])

        data['category'] = self.category.pk
        response = self.client.get(reverse('spirit:search:search'),
                                   data)
        self.assertEqual(len(response.context['page']), 1)

    def test_search_removed_topics(self):
        """
        Should not include removed topics
        """
        utils.login(self)
        data = {'q': 'spirit search'}

        response = self.client.get(
            reverse('spirit:search:search'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page']), 1)

        self.topic.is_removed = True
        self.topic.save()
        rebuild_index()
        response = self.client.get(
            reverse('spirit:search:search'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page']), 0)



class SearchFormTest(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_basic_search(self):
        data = {'q': 'foobar', }
        form = BasicSearchForm(data)
        self.assertEqual(form.is_valid(), True)

    def test_basic_search_invalid_too_short(self):
        data = {'q': 'a' * (settings.ST_SEARCH_QUERY_MIN_LEN - 1), }
        form = BasicSearchForm(data)
        self.assertEqual(form.is_valid(), False)

    def test_advanced_search(self):
        data = {'q': 'foobar', }
        form = AdvancedSearchForm(data)
        self.assertEqual(form.is_valid(), True)

    def test_advanced_search_invalid_too_short(self):
        data = {'q': 'a' * (settings.ST_SEARCH_QUERY_MIN_LEN - 1), }
        form = AdvancedSearchForm(data)
        self.assertEqual(form.is_valid(), False)


class SearchTemplateTagTests(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_render_search_form(self):
        """
        should display the basic search form
        """
        Template(
            "{% load spirit_tags %}"
            "{% render_search_form %}"
        ).render(Context())
        context = render_search_form()
        self.assertIsInstance(context['form'], BasicSearchForm)
