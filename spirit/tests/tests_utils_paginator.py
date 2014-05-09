#-*- coding: utf-8 -*-

from django.core.cache import cache
from django.test import TestCase, RequestFactory
from django.template import Template, Context, TemplateSyntaxError
from django.test.utils import override_settings
from django.http import Http404
from django.core.paginator import Page, Paginator

import utils
from spirit.models.comment import Comment

from spirit.utils.paginator.yt_paginator import YTPaginator, InvalidPage, YTPage
from spirit.utils import paginator
from spirit.utils.paginator import infinite_paginator
from spirit.templatetags.tags.utils.paginator import yt_paginator_autopaginate, paginator_autopaginate, \
    render_yt_paginator, render_paginator


class UtilsPaginatorTest(TestCase):

    def setUp(self):
        cache.clear()

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
        cache.clear()
        self.user = utils.create_user()
        self.topic = utils.create_topic(utils.create_category())

        for _ in xrange(300):
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
        cache.clear()
        self.user = utils.create_user()
        self.topic = utils.create_topic(utils.create_category())

        for _ in xrange(300):
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

        for page_num in xrange(1, 30 + 1):
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
        yt_paginator = YTPaginator(list(xrange(0, 100)), per_page=10)

        page = yt_paginator.page(1)
        self.assertListEqual(list(page.page_range), [1, 2, 3, 4, 5, 6, 7])

        page = yt_paginator.page(4)
        self.assertListEqual(list(page.page_range), [1, 2, 3, 4, 5, 6, 7])

        page = yt_paginator.page(7)
        self.assertListEqual(list(page.page_range), [4, 5, 6, 7, 8, 9, 10])

        page = yt_paginator.page(10)
        self.assertListEqual(list(page.page_range), [4, 5, 6, 7, 8, 9, 10])

        # 2 pages
        yt_paginator = YTPaginator(list(xrange(0, 20)), per_page=10)

        page = yt_paginator.page(1)
        self.assertListEqual(list(page.page_range), [1, 2])

        page = yt_paginator.page(2)
        self.assertListEqual(list(page.page_range), [1, 2])


class UtilsYTPaginatorTemplateTagsTests(TestCase):

    def setUp(self):
        cache.clear()

    def tests_yt_paginator_autopaginate_tag(self):
        """
        Minimal test to check it works
        """
        req = RequestFactory().get('/')
        out = Template(
            "{% load spirit_tags %}"
            "{% yt_paginator_autopaginate items per_page=5 as page %}"
            "{% for p in page %}"
            "{{ p }}"
            "{% endfor %}"
        ).render(Context({'request': req, 'items': list(xrange(0, 20)), }))
        self.assertEqual(out, "01234")

    def tests_yt_paginator_autopaginate(self):
        # first page
        req = RequestFactory().get('/')
        context = {'request': req, }
        items = list(xrange(0, 20))
        page = yt_paginator_autopaginate(context, items, per_page=10, page_var="val")
        self.assertIsInstance(page, YTPage)
        self.assertEqual(list(page), items[:10])

        # second page
        req = RequestFactory().get('/?val=2')
        context = {'request': req, }
        page = yt_paginator_autopaginate(context, items, per_page=10, page_var="val")
        self.assertEqual(list(page), items[10:20])

        # invalid page
        req = RequestFactory().get('/?val=3')
        context = {'request': req, }
        self.assertRaises(Http404, yt_paginator_autopaginate,
                          context, items, per_page=10, page_var="val")

        # empty first page
        req = RequestFactory().get('/')
        context = {'request': req, }
        page = yt_paginator_autopaginate(context, [], per_page=10, page_var="val")
        self.assertListEqual(list(page), [])

    def tests_render_yt_paginator_tag(self):
        """
        Minimal test to check it works
        """
        req = RequestFactory().get('/')
        items = list(xrange(0, 20))
        page = YTPaginator(items, per_page=10).page(1)
        out = Template(
            "{% load spirit_tags %}"
            "{% render_yt_paginator page %}"
        ).render(Context({'request': req, 'page': page, }))

    def tests_render_yt_paginator(self):
        req = RequestFactory().get('/')
        context = {'request': req, }
        items = list(xrange(0, 20))
        page = YTPaginator(items, per_page=10).page(1)
        res = render_yt_paginator(context, page)
        self.assertDictEqual(res, {"page": page,
                                   "page_var": 'page',
                                   "hashtag": '',
                                   "extra_query": ''})

    def tests_render_yt_paginator_extra(self):
        req = RequestFactory().get('/?foo_page=1&extra=foo')
        context = {'request': req, }
        items = list(xrange(0, 20))
        page = YTPaginator(items, per_page=10).page(1)
        res = render_yt_paginator(context, page, page_var='foo_page', hashtag="c20")
        self.assertDictEqual(res, {"page": page,
                                   "page_var": 'foo_page',
                                   "hashtag": '#c20',
                                   "extra_query": '&extra=foo'})



class UtilsPaginatorTemplateTagsTests(TestCase):

    def setUp(self):
        cache.clear()

    def tests_paginator_autopaginate_tag(self):
        """
        Minimal test to check it works
        """
        req = RequestFactory().get('/')
        out = Template(
            "{% load spirit_tags %}"
            "{% paginator_autopaginate items per_page=5 as page %}"
            "{% for p in page %}"
            "{{ p }}"
            "{% endfor %}"
        ).render(Context({'request': req, 'items': list(xrange(0, 20)), }))
        self.assertEqual(out, "01234")

    def tests_paginator_autopaginate(self):
        # first page
        req = RequestFactory().get('/')
        context = {'request': req, }
        items = list(xrange(0, 20))
        page = paginator_autopaginate(context, items, per_page=10, page_var="val")
        self.assertIsInstance(page, Page)
        self.assertEqual(list(page), items[:10])

        # second page
        req = RequestFactory().get('/?val=2')
        context = {'request': req, }
        page = paginator_autopaginate(context, items, per_page=10, page_var="val")
        self.assertEqual(list(page), items[10:20])

        # invalid page
        req = RequestFactory().get('/?val=3')
        context = {'request': req, }
        self.assertRaises(Http404, paginator_autopaginate,
                          context, items, per_page=10, page_var="val")

        # empty first page
        req = RequestFactory().get('/')
        context = {'request': req, }
        page = paginator_autopaginate(context, [], per_page=10, page_var="val")
        self.assertListEqual(list(page), [])

    def tests_render_paginator_tag(self):
        """
        Minimal test to check it works
        """
        req = RequestFactory().get('/')
        items = list(xrange(0, 20))
        page = Paginator(items, per_page=10).page(1)
        out = Template(
            "{% load spirit_tags %}"
            "{% render_paginator page %}"
        ).render(Context({'request': req, 'page': page, }))

    def tests_render_paginator(self):
        req = RequestFactory().get('/')
        context = {'request': req, }
        items = list(xrange(0, 20))
        page = Paginator(items, per_page=10).page(1)
        res = render_paginator(context, page)
        self.assertDictEqual(res, {"page": page,
                                   "page_var": 'page',
                                   "hashtag": '',
                                   "extra_query": ''})

    def tests_render_paginator_extra(self):
        req = RequestFactory().get('/?foo_page=1&extra=foo')
        context = {'request': req, }
        items = list(xrange(0, 20))
        page = Paginator(items, per_page=10).page(1)
        res = render_paginator(context, page, page_var='foo_page', hashtag="c20")
        self.assertDictEqual(res, {"page": page,
                                   "page_var": 'foo_page',
                                   "hashtag": '#c20',
                                   "extra_query": '&extra=foo'})