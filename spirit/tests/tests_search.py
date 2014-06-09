#-*- coding: utf-8 -*-

from django.test import TestCase
from django.test.utils import override_settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template import Template, Context, TemplateSyntaxError
from django.conf import settings
from django.core.management import call_command

import haystack
from haystack.query import SearchQuerySet

import utils

from spirit.models.topic import Topic
from spirit.forms.search import BasicSearchForm, BaseSearchForm, AdvancedSearchForm
from spirit.templatetags.tags.search import render_search_form
from spirit.search_indexes import TopicIndex


HAYSTACK_TEST = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}


class SearchTopicIndexTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()

    def test_index_queryset_excludes_private_topics(self):
        """
        index_queryset should exclude private topics
        """
        private = utils.create_private_topic()
        self.assertEqual(len(TopicIndex().index_queryset()), 0)

        category = utils.create_category()
        topic = utils.create_topic(category)
        self.assertEqual(len(TopicIndex().index_queryset()), 1)

    def test_indexing_excludes_private_topics(self):
        """
        rebuild_index command should exclude private topics
        """
        private = utils.create_private_topic()
        category = utils.create_category()
        topic = utils.create_topic(category)
        call_command("rebuild_index", interactive=False)

        sqs = SearchQuerySet().models(Topic)
        self.assertQuerysetEqual([s.object for s in sqs], map(repr, [topic, ]))


class SearchViewTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        # TODO: simple backend wont work on django +1.6 coz of a bug on haystack 2.1
        #self.connections = haystack.connections
        #haystack.connections = haystack.loading.ConnectionHandler(HAYSTACK_TEST)

        cache.clear()
        self.user = utils.create_user()
        self.category = utils.create_category()
        self.topic = utils.create_topic(category=self.category, user=self.user, title="spirit search test")
        self.topic2 = utils.create_topic(category=self.category, user=self.user, title="foo")

        call_command("rebuild_index", interactive=False)

    #def tearDown(self):
        #haystack.connections = self.connections

    def test_advanced_search_detail(self):
        """
        advanced search by topic
        """
        utils.login(self)
        response = self.client.get(reverse('spirit:search'))
        self.assertEqual(response.status_code, 200)

    def test_advanced_search_topics(self):
        """
        advanced search by topic
        """
        utils.login(self)
        data = {'q': 'spirit search', }
        response = self.client.get(reverse('spirit:search'),
                                   data)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual([s.object for s in response.context['page']], map(repr, [self.topic, ]))

    def test_advanced_search_in_category(self):
        """
        search by topic in category
        """
        utils.login(self)
        category = utils.create_category()
        data = {'q': 'spirit search', 'category': category.pk}
        response = self.client.get(reverse('spirit:search'),
                                   data)
        self.assertQuerysetEqual(response.context['page'], [])

        data['category'] = self.category.pk
        response = self.client.get(reverse('spirit:search'),
                                   data)
        self.assertEqual(len(response.context['page']), 1)


class SearchFormTest(TestCase):

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()

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

    fixtures = ['spirit_init.json', ]

    def setUp(self):
        cache.clear()

    def test_render_search_form(self):
        """
        should display the basic search form
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% render_search_form %}"
        ).render(Context())
        context = render_search_form()
        self.assertIsInstance(context['form'], BasicSearchForm)