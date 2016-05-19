# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase, RequestFactory
from django.template import Template, Context
from django.test.utils import override_settings
from django.http import Http404
from django.core.paginator import Page, Paginator

from ..tests import utils
from ...comment.models import Comment
from ..utils import paginator
from ..utils.paginator import YTPaginator, InvalidPage, YTPage
from ..utils.paginator import infinite_paginator, paginate, yt_paginate
from ..tags.paginator import render_paginator
from ..tags import paginator as ttag_paginator


class UtilsPaginatorTest(TestCase):

    def setUp(self):
        utils.cache_clear()

    def test_paginator_page(self):
        per_page = 15
        obj_number = 1
        self.assertEqual(paginator.get_page_number(obj_number=obj_number, per_page=per_page), 1)
        obj_number = per_page
        self.assertEqual(paginator.get_page_number(obj_number=obj_number, per_page=per_page), 1)
        obj_number = per_page - 1
        self.assertEqual(paginator.get_page_number(obj_number=obj_number, per_page=per_page), 1)
        obj_number = per_page + 1
        self.assertEqual(paginator.get_page_number(obj_number=obj_number, per_page=per_page), 2)

    def test_paginator_url(self):
        per_page = 15
        obj_number = 1
        page_var = "page"
        url = "/path/"
        first_page = url + '#c' + str(obj_number)
        self.assertEqual(paginator.get_url(url, obj_number, per_page, page_var), first_page)
        obj_number = 16
        expected = '%(url)s?%(page_var)s=%(page_num)s#c%(obj_number)s' % {'url': url,
                                                                          'page_var': page_var,
                                                                          'page_num': 2,
                                                                          'obj_number': obj_number}
        self.assertEqual(paginator.get_url(url, obj_number, per_page, page_var), expected)


class UtilsInfinitePaginatorTest(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.topic = utils.create_topic(utils.create_category())

        for _ in range(300):
            utils.create_comment(user=self.user, topic=self.topic)

        self.queryset = Comment.objects.all().order_by("-pk")

    def test_paginate(self):
        # first page
        req = RequestFactory().get('/')
        page = infinite_paginator.paginate(req, self.queryset, per_page=15, lookup_field="pk")
        page_last_pk = list(self.queryset[:15])[-1].pk
        self.assertEqual(page.next_page_pk(), page_last_pk)

        # second page
        page_last_pk = list(self.queryset[:15])[-1].pk
        req = RequestFactory().get('/?id=%s' % page_last_pk)
        page = infinite_paginator.paginate(req, self.queryset, per_page=15, lookup_field="pk", page_var='id')
        second_page_last_pk = list(self.queryset[15:30])[-1].pk
        self.assertEqual(page.next_page_pk(), second_page_last_pk)

        # invalid (id) page
        last_pk = self.queryset.order_by("pk").last().pk
        req = RequestFactory().get('/?id=%s' % (last_pk + 1))
        self.assertRaises(Http404, infinite_paginator.paginate,
                          req, self.queryset, per_page=15, lookup_field="pk", page_var='id')

        # empty page
        valid_pk = self.queryset.last().pk
        req = RequestFactory().get('/?id=%s' % valid_pk)
        self.assertRaises(Http404, infinite_paginator.paginate,
                          req, self.queryset.none(), per_page=15, lookup_field="pk", page_var='id')

        # empty first page
        req = RequestFactory().get('/')
        page = infinite_paginator.paginate(req, self.queryset.none(), per_page=15, lookup_field="pk")
        self.assertEqual(len(page), 0)


class UtilsYTPaginatorTests(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user()
        self.topic = utils.create_topic(utils.create_category())

        for _ in range(300):
            utils.create_comment(user=self.user, topic=self.topic)

        self.queryset = Comment.objects.all()

    def test_yt_paginator_page(self):
        yt_paginator = YTPaginator(self.queryset, per_page=10)
        page = yt_paginator.page(1)
        self.assertEqual(page.number, 1)
        self.assertListEqual([i for i in page], list(self.queryset[:10]))

        # empty first page
        yt_paginator = YTPaginator(self.queryset.none(), per_page=10)
        self.assertListEqual([i for i in yt_paginator.page(1)], [])

    def test_yt_paginator_page_invalid(self):
        yt_paginator = YTPaginator(self.queryset, per_page=10)
        self.assertRaises(InvalidPage, lambda: yt_paginator.page("one"))
        self.assertRaises(InvalidPage, lambda: yt_paginator.page(-1))
        self.assertRaises(InvalidPage, lambda: yt_paginator.page(5000))

    def tests_yt_paginator_num_pages(self):
        yt_paginator = YTPaginator(self.queryset, per_page=10)
        page = yt_paginator.page(1)

        for page_num in range(1, 30 + 1):
            page._num_pages = None
            page._max_pages = page_num
            self.assertEqual(page.num_pages, page_num)

        page._num_pages = None
        page._max_pages = 8
        self.assertEqual(page.num_pages, 8)

        page._num_pages = None
        page._max_pages = 3000
        self.assertEqual(page.num_pages, 30)

    @override_settings(ST_YT_PAGINATOR_PAGE_RANGE=3)
    def test_yt_paginator_page_range(self):
        # 10 pages
        yt_paginator = YTPaginator(list(range(0, 100)), per_page=10)

        page = yt_paginator.page(1)
        self.assertListEqual(list(page.page_range), [1, 2, 3, 4, 5, 6, 7])

        page = yt_paginator.page(4)
        self.assertListEqual(list(page.page_range), [1, 2, 3, 4, 5, 6, 7])

        page = yt_paginator.page(7)
        self.assertListEqual(list(page.page_range), [4, 5, 6, 7, 8, 9, 10])

        page = yt_paginator.page(10)
        self.assertListEqual(list(page.page_range), [4, 5, 6, 7, 8, 9, 10])

        # 2 pages
        yt_paginator = YTPaginator(list(range(0, 20)), per_page=10)

        page = yt_paginator.page(1)
        self.assertListEqual(list(page.page_range), [1, 2])

        page = yt_paginator.page(2)
        self.assertListEqual(list(page.page_range), [1, 2])


class UtilsYTPaginatorTemplateTagsTests(TestCase):

    def setUp(self):
        utils.cache_clear()

    def tests_yt_paginate(self):
        # first page
        items = list(range(0, 20))
        page = yt_paginate(items, per_page=10)
        self.assertIsInstance(page, YTPage)
        self.assertEqual(list(page), items[:10])

        # second page
        page = yt_paginate(items, per_page=10, page_number=2)
        self.assertEqual(list(page), items[10:20])

        # invalid page
        self.assertRaises(Http404, yt_paginate,
                          items, per_page=10, page_number=99)

        # empty first page
        page = yt_paginate([], per_page=10)
        self.assertListEqual(list(page), [])

    def tests_render_yt_paginator(self):
        def mock_render(template, context):
            return template, context

        req = RequestFactory().get('/')
        context = {'request': req, }
        items = list(range(0, 20))
        page = YTPaginator(items, per_page=10).page(1)

        org_render, ttag_paginator.render_to_string = ttag_paginator.render_to_string, mock_render
        try:
            template, context2 = render_paginator(context, page)
            self.assertDictEqual(context2, {"page": page,
                                            "page_var": 'page',
                                            "hashtag": '',
                                            "extra_query": ''})
            self.assertEqual(template, "spirit/utils/paginator/_yt_paginator.html")
        finally:
            ttag_paginator.render_to_string = org_render

    def tests_render_yt_paginator_extra(self):
        def mock_render(template, context):
            return template, context

        req = RequestFactory().get('/?foo_page=1&extra=foo')
        context = {'request': req, }
        items = list(range(0, 20))
        page = YTPaginator(items, per_page=10).page(1)

        org_render, ttag_paginator.render_to_string = ttag_paginator.render_to_string, mock_render
        try:
            template, context2 = render_paginator(context, page, page_var='foo_page', hashtag="c20")
            self.assertDictEqual(context2, {"page": page,
                                            "page_var": 'foo_page',
                                            "hashtag": '#c20',
                                            "extra_query": '&extra=foo'})
            self.assertEqual(template, "spirit/utils/paginator/_yt_paginator.html")
        finally:
            ttag_paginator.render_to_string = org_render


class UtilsPaginatorTemplateTagsTests(TestCase):

    def setUp(self):
        utils.cache_clear()

    def tests_paginate(self):
        # first page
        items = list(range(0, 20))
        page = paginate(items, per_page=10)
        self.assertIsInstance(page, Page)
        self.assertEqual(list(page), items[:10])

        # second page
        page = paginate(items, per_page=10, page_number=2)
        self.assertEqual(list(page), items[10:20])

        # invalid page
        self.assertRaises(Http404, paginate,
                          items, per_page=10, page_number=99)

        # empty first page
        page = paginate([], per_page=10)
        self.assertListEqual(list(page), [])

    def tests_render_paginator_tag(self):
        """
        Minimal test to check it works
        """
        req = RequestFactory().get('/')
        items = list(range(0, 20))
        page = Paginator(items, per_page=10).page(1)
        Template(
            "{% load spirit_tags %}"
            "{% render_paginator page %}"
        ).render(Context({'request': req, 'page': page, }))

    def tests_render_paginator(self):
        def mock_render(template, context):
            return template, context

        req = RequestFactory().get('/')
        context = {'request': req, }
        items = list(range(0, 20))
        page = Paginator(items, per_page=10).page(1)

        org_render, ttag_paginator.render_to_string = ttag_paginator.render_to_string, mock_render
        try:
            template, context2 = render_paginator(context, page)
            self.assertDictEqual(context2, {"page": page,
                                            "page_var": 'page',
                                            "hashtag": '',
                                            "extra_query": ''})
            self.assertEqual(template, "spirit/utils/paginator/_paginator.html")
        finally:
            ttag_paginator.render_to_string = org_render

    def tests_render_paginator_extra(self):
        def mock_render(template, context):
            return template, context

        req = RequestFactory().get('/?foo_page=1&extra=foo')
        context = {'request': req, }
        items = list(range(0, 20))
        page = Paginator(items, per_page=10).page(1)

        org_render, ttag_paginator.render_to_string = ttag_paginator.render_to_string, mock_render
        try:
            template, context2 = render_paginator(context, page, page_var='foo_page', hashtag="c20")
            self.assertDictEqual(context2, {"page": page,
                                            "page_var": 'foo_page',
                                            "hashtag": '#c20',
                                            "extra_query": '&extra=foo'})
            self.assertEqual(template, "spirit/utils/paginator/_paginator.html")
        finally:
            ttag_paginator.render_to_string = org_render
