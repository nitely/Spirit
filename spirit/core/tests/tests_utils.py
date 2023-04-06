# -*- coding: utf-8 -*-

import datetime
import json
import os
from urllib.parse import unquote

from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.template import Template, Context
from django.utils import translation
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import get_user_model

from ..conf import settings
from ...category.models import Category
from .. import utils
from ..utils.forms import NestedModelChoiceField
from ..utils.decorators import moderator_required, administrator_required
from ..tags import time as ttags_utils
from . import utils as test_utils
from ..tags.messages import render_messages

User = get_user_model()
utc = datetime.timezone.utc


class UtilsTests(TestCase):

    def setUp(self):
        test_utils.cache_clear()

    def test_render_form_errors(self):
        """
        return form errors string
        """
        class MockForm:
            non_field_errors = ["error1", ]
            hidden_fields = [{'errors': "error2", }, ]
            visible_fields = [{'errors': "error3", }, ]

        res = utils.render_form_errors(MockForm())
        lines = [line.strip() for line in res.splitlines()]
        self.assertEqual(
            "".join(lines),
            '<ul class="errorlist"><li>error1</li>'
            '<li>error2</li><li>error3</li></ul>')

    def test_json_response(self):
        """
        return json_response
        """
        res = utils.json_response()
        self.assertIsInstance(res, HttpResponse)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/json')
        self.assertDictEqual(json.loads(res.content.decode('utf-8')), {})

        res = utils.json_response({"foo": "bar"})
        self.assertDictEqual(
            json.loads(res.content.decode('utf-8')),
            {"foo": "bar"})

        res = utils.json_response(status=404)
        self.assertEqual(res.status_code, 404)

    def test_mkdir_p(self):
        """
        mkdir -p
        """
        # Empty path should raise an exception
        self.assertRaises(OSError, utils.mkdir_p, "")

        # Try to create an existing dir should do nothing
        self.assertTrue(os.path.isdir(settings.BASE_DIR))
        utils.mkdir_p(settings.BASE_DIR)

        # Create path tree
        # setup
        path = os.path.join(settings.BASE_DIR, "test_foo")
        sub_path = os.path.join(path, "bar")
        self.assertFalse(os.path.isdir(sub_path))
        self.assertFalse(os.path.isdir(path))
        # test
        utils.mkdir_p(sub_path)
        self.assertTrue(os.path.isdir(sub_path))
        # clean up
        os.rmdir(sub_path)
        os.rmdir(path)

    def test_pushd(self):
        """
        pushd bash like
        """
        current_dir = {'dir': '.'}

        class MockOS:
            @classmethod
            def chdir(cls, new_dir):
                current_dir['dir'] = new_dir

            @classmethod
            def getcwd(cls):
                return current_dir['dir']

        org_os, utils.os = utils.os, MockOS
        try:
            with utils.pushd('./my_dir'):
                self.assertEqual(current_dir['dir'], './my_dir')

                with utils.pushd('./my_dir/my_other_dir'):
                    self.assertEqual(current_dir['dir'], './my_dir/my_other_dir')

                self.assertEqual(current_dir['dir'], './my_dir')

            self.assertEqual(current_dir['dir'], '.')
        finally:
            utils.os = org_os


# Mock out datetime in some tests so they don't fail occasionally when they
# run too slow. Use a fixed datetime for datetime.now(). DST change in
# America/Chicago (the default time zone) happened on March 11th in 2012.
# Note: copy from django.contrib.humanize.tests.py

now = datetime.datetime(2012, 3, 9, 22, 30)


class MockDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        if tz is None or tz.utcoffset(now) is None:
            return now
        else:
            # equals now.replace(tzinfo=utc)
            return now.replace(tzinfo=tz) + tz.utcoffset(now)


class UtilsTemplateTagTests(TestCase):

    def test_shortnaturaltime(self):
        """"""
        class naive(datetime.tzinfo):
            def utcoffset(self, dt):
                return None

        def render(date):
            t = Template(
                '{% load spirit_tags %}'
                '{{ date|shortnaturaltime }}')
            return t.render(Context({'date': date, }))

        orig_humanize_datetime, ttags_utils.datetime = ttags_utils.datetime, MockDateTime
        try:
            with translation.override('en'):
                with override_settings(USE_TZ=True):
                    self.assertEqual(render(now), "now")
                    self.assertEqual(render(now.replace(tzinfo=naive())), "now")
                    self.assertEqual(render(now.replace(tzinfo=utc)), "now")
                    self.assertEqual(render(now - datetime.timedelta(seconds=1)), "1s")
                    self.assertEqual(render(now - datetime.timedelta(minutes=1)), "1m")
                    self.assertEqual(render(now - datetime.timedelta(hours=1)), "1h")
                    self.assertEqual(render(now - datetime.timedelta(days=1)), "8 Mar")
                    # django 2.2 and 3.0 compat
                    self.assertTrue(
                        render(now - datetime.timedelta(days=69)) == "31 Dec &#x27;11"
                        or render(now - datetime.timedelta(days=69)) == "31 Dec &#39;11")

                    # Tests it uses localtime
                    # This is 2012-03-08HT19:30:00-06:00 in America/Chicago
                    dt = datetime.datetime(2011, 3, 9, 1, 30, tzinfo=utc)

                    # Overriding TIME_ZONE won't work when timezone.activate
                    # was called in some point before (middleware)
                    timezone.deactivate()

                    with override_settings(TIME_ZONE="America/Chicago"):
                        # django 2.2 and 3.0 compat
                        self.assertTrue(
                            render(dt) == "8 Mar &#x27;11"
                            or render(dt) == "8 Mar &#39;11")
        finally:
            ttags_utils.datetime = orig_humanize_datetime

    def test_render_messages(self):
        """
        Test messages grouped by level
        """
        # TODO: test template rendering
        class MockMessage:
            def __init__(self, level, message):
                self.level = level
                self.tags = messages.DEFAULT_TAGS[level]
                self.message = message

        m1 = MockMessage(messages.constants.ERROR, 'error 1')
        m2 = MockMessage(messages.constants.ERROR, 'error 2')
        m3 = MockMessage(messages.constants.INFO, 'info 3')
        res = render_messages([m1, m2, m3])
        self.assertDictEqual(
            dict(res['messages_grouped']),
            {'error': [m1, m2], 'info': [m3, ]})

    def test_social_share(self):
        """
        Test social share tags with unicode input
        """
        t = Template(
            '{% load spirit_tags %}'
            '{% get_facebook_share_url url="/á/foo bar/" title="á" %}'
            '{% get_twitter_share_url url="/á/foo bar/" title="á" %}'
            '{% get_email_share_url url="/á/foo bar/" title="á" %}'
            '{% get_share_url url="/á/foo bar/" %}')
        res = t.render(Context(
            {'request': RequestFactory().get('/')},
            autoescape=False))
        self.assertEqual(
            res.strip(),
            "https://www.facebook.com/sharer/sharer.php?u=http%3A%2F%2Ftestserver"
            "%2F%25C3%25A1%2Ffoo%2520bar%2F&t=%C3%A1"
            "https://twitter.com/share?url=http%3A%2F%2Ftestserver%2F%25C3%25A1%2F"
            "foo%2520bar%2F&text=%C3%A1"
            "mailto:?body=http%3A%2F%2Ftestserver%2F%25C3%25A1%2Ffoo%2520bar%2F"
            "&subject=%C3%A1&to="
            "http://testserver/%C3%A1/foo%20bar/")

    def test_social_share_twitter_length(self):
        """
        Twitter allows up to 140 chars, takes 23 for urls (https)
        """
        # so this unicode title when is *url-quoted* becomes really large, like 1000 chars large,
        # browsers support up to 2000 chars for an address, we should be fine.
        long_title = "á" * 150
        t = Template(
            '{% load spirit_tags %}'
            '{% get_twitter_share_url url="/foo/" title=long_title %}')
        res = t.render(Context(
            {'request': RequestFactory().get('/'),
             'long_title': long_title}))
        url = unquote(res.strip())
        self.assertEqual(len(url.split("text=")[-1]) + 23, 139)  # 140 for https


class UtilsFormsTests(TestCase):

    def test_nested_model_choise_form(self):
        """
        NestedModelChoiceField
        """
        Category.objects.all().delete()

        category = test_utils.create_category()
        category2 = test_utils.create_category()
        subcategory = test_utils.create_subcategory(category)
        field = NestedModelChoiceField(
            queryset=Category.objects.all(),
            related_name='category_set',
            parent_field='parent_id',
            label_field='title')
        self.assertSequenceEqual(
            list(field.choices),
            [('', '---------'),
             (category.pk, '%s' % category.title),
             (subcategory.pk, '--- %s' % subcategory.title),
             (category2.pk, '%s' % category2.title)])


class UtilsDecoratorsTests(TestCase):

    def setUp(self):
        test_utils.cache_clear()
        self.user = test_utils.create_user()

    def test_moderator_required(self):
        """
        Tests the user is logged in and is also a moderator
        """
        @moderator_required
        def view(req):
            pass

        req = RequestFactory().get('/')

        req.user = AnonymousUser()
        self.assertIsInstance(view(req), HttpResponseRedirect)

        req.user = self.user
        req.user.st.is_moderator = False
        self.assertRaises(PermissionDenied, view, req)

        req.user.st.is_moderator = True
        self.assertIsNone(view(req))

    def test_administrator_required(self):
        """
        Tests the user is logged in and is also an admin
        """
        @administrator_required
        def view(req):
            pass

        req = RequestFactory().get('/')

        req.user = AnonymousUser()
        self.assertIsInstance(view(req), HttpResponseRedirect)

        req.user = self.user
        req.user.st.is_administrator = False
        self.assertRaises(PermissionDenied, view, req)

        req.user.st.is_administrator = True
        self.assertIsNone(view(req))
