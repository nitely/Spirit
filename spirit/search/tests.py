# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime

from django.test import TestCase, override_settings
from django.urls import reverse
from django.template import Template, Context
from django.core.management import call_command
from django.template.loader import render_to_string
from django.utils import timezone

from haystack.query import SearchQuerySet
from djconfig.utils import override_djconfig

from ..core.conf import settings
from ..core.tests import utils
from ..topic.models import Topic
from .forms import BasicSearchForm, AdvancedSearchForm
from .tags import render_search_form
from .search_indexes import TopicIndex


def rebuild_index():
    call_command("rebuild_index", verbosity=0, interactive=False)


class SearchTopicIndexTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.topic_sqs = SearchQuerySet().models(Topic)
        self.now = timezone.now()
        self.yesterday = timezone.now() - datetime.timedelta(days=1)
        self.tomorrow = timezone.now() + datetime.timedelta(days=1)

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

    def test_indexing_text_include_comments(self):
        """
        Should include topic title and all comments
        """
        category = utils.create_category()
        topic = utils.create_topic(category, title='my title')
        utils.create_comment(topic=topic, comment_html='<span>foo</span>')
        utils.create_comment(topic=topic, comment_html='<b>bar</b>')
        rebuild_index()
        self.assertEqual(len(self.topic_sqs.all()), 1)
        self.assertEqual(
            len(self.topic_sqs.filter(text='my title foo bar')), 1)
        self.assertEqual(
            len(self.topic_sqs.filter(text='bar')), 1)
        self.assertEqual(
            len(self.topic_sqs.filter(text='<b>')), 0)
        self.assertEqual(
            len(self.topic_sqs.filter(text='span')), 0)

    def test_indexing_text_template(self):
        """
        Should include topic title and all comments
        """
        category = utils.create_category()
        topic = utils.create_topic(category, title='my title')
        utils.create_comment(topic=topic, comment_html='<span>foo</span>')
        utils.create_comment(topic=topic, comment_html='<b>bar</b>')
        self.assertEqual(
            render_to_string(
                'search/indexes/spirit_topic/topic_text.txt',
                context={'object': topic}),
            'my title\n\nbar\n\nfoo\n\n')

    def test_indexing_build_queryset_by_topic(self):
        """
        Should update topics based on modified times
        """
        main_category = utils.create_category(
            reindex_at=self.yesterday)
        category = utils.create_category(
            parent=main_category, reindex_at=self.yesterday)
        topic = utils.create_topic(
            category,
            reindex_at=self.yesterday, last_active=self.yesterday)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now)), 0)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.tomorrow)), 0)

        topic.reindex_at = self.tomorrow
        topic.save()
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now)), 1)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.tomorrow)), 1)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.now)), 0)

    def test_indexing_build_queryset_by_comment(self):
        """
        Should update topics based on modified times
        """
        main_category = utils.create_category(
            reindex_at=self.yesterday)
        category = utils.create_category(
            parent=main_category, reindex_at=self.yesterday)
        topic = utils.create_topic(
            category,
            reindex_at=self.yesterday, last_active=self.yesterday)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now)), 0)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.tomorrow)), 0)

        topic.last_active = self.tomorrow
        topic.save()
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now)), 1)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.tomorrow)), 1)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.now)), 0)

    def test_indexing_build_queryset_by_category(self):
        """
        Should update topics based on modified times
        """
        main_category = utils.create_category(
            reindex_at=self.yesterday)
        category = utils.create_category(
            parent=main_category, reindex_at=self.yesterday)
        utils.create_topic(
            category,
            reindex_at=self.yesterday, last_active=self.yesterday)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now)), 0)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.tomorrow)), 0)

        category.reindex_at = self.tomorrow
        category.save()
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now)), 1)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.tomorrow)), 1)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.now)), 0)

    def test_indexing_build_queryset_by_subcategory(self):
        """
        Should update topics based on modified times
        """
        main_category = utils.create_category(
            reindex_at=self.yesterday)
        category = utils.create_category(
            parent=main_category, reindex_at=self.yesterday)
        utils.create_topic(
            category,
            reindex_at=self.yesterday, last_active=self.yesterday)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now)), 0)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.tomorrow)), 0)

        main_category.reindex_at = self.tomorrow
        main_category.save()
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now)), 1)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.tomorrow)), 1)
        self.assertEqual(
            len(TopicIndex().build_queryset(start_date=self.now, end_date=self.now)), 0)


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

    @override_settings(ST_SEARCH_QUERY_MIN_LEN=1)
    def test_basic_search_exclude_removed_topics(self):
        """
        Should not include removed topics
        """
        category = utils.create_category()
        topic = utils.create_topic(category, title='sup?')
        rebuild_index()
        data = {'q': 'sup'}
        form = BasicSearchForm(data)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(len(form.search()), 1)

        topic.is_removed = True
        topic.save()
        rebuild_index()
        form = BasicSearchForm(data)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(len(form.search()), 0)

    def test_advanced_search(self):
        data = {'q': 'foobar', }
        form = AdvancedSearchForm(data)
        self.assertEqual(form.is_valid(), True)

    def test_advanced_search_invalid_too_short(self):
        data = {'q': 'a' * (settings.ST_SEARCH_QUERY_MIN_LEN - 1), }
        form = AdvancedSearchForm(data)
        self.assertEqual(form.is_valid(), False)

    @override_settings(ST_SEARCH_QUERY_MIN_LEN=1)
    def test_advanced_search_exclude_removed_topics(self):
        """
        Should not include removed topics
        """
        category = utils.create_category()
        topic = utils.create_topic(category, title='sup?')
        rebuild_index()
        data = {'q': 'sup'}
        form = AdvancedSearchForm(data)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(len(form.search()), 1)

        topic.is_removed = True
        topic.save()
        rebuild_index()
        form = AdvancedSearchForm(data)
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(len(form.search()), 0)


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
