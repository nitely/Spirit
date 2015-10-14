# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import json
import os

from django.core.cache import cache
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.template import Template, Context
from django.utils import translation
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.conf import settings
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.timezone import utc
from django.utils.http import urlunquote
from django.contrib.auth import get_user_model

from ...category.models import Category
from .. import utils
from ..utils.forms import NestedModelChoiceField
from ..utils.timezone import TIMEZONE_CHOICES
from ..utils.decorators import moderator_required, administrator_required
from ...user.utils.tokens import UserActivationTokenGenerator, UserEmailChangeTokenGenerator
from ...user.utils.email import send_activation_email, send_email_change_email, sender
from ...user.utils import email
from ..tags import time as ttags_utils
from ..tests import utils as test_utils
from ..tags.messages import render_messages

User = get_user_model()


class UtilsTests(TestCase):

    def setUp(self):
        cache.clear()

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
        self.assertEqual("".join(lines), '<ul class="errorlist"><li>error1</li><li>error2</li><li>error3</li></ul>')

    def test_json_response(self):
        """
        return json_response
        """
        res = utils.json_response()
        self.assertIsInstance(res, HttpResponse)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/json')
        self.assertDictEqual(json.loads(res.content.decode('utf-8')), {})

        res = utils.json_response({"foo": "bar", })
        self.assertDictEqual(json.loads(res.content.decode('utf-8')), {"foo": "bar", })

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
            t = Template('{% load spirit_tags %}'
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
                    self.assertEqual(render(now - datetime.timedelta(days=69)), "31 Dec &#39;11")

                    # Tests it uses localtime
                    # This is 2012-03-08HT19:30:00-06:00 in America/Chicago
                    dt = datetime.datetime(2011, 3, 9, 1, 30, tzinfo=utc)

                    # Overriding TIME_ZONE won't work when timezone.activate
                    # was called in some point before (middleware)
                    timezone.deactivate()

                    with override_settings(TIME_ZONE="America/Chicago"):
                        self.assertEqual(render(dt), "8 Mar &#39;11")
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
        self.assertDictEqual(dict(res['messages_grouped']), {'error': [m1, m2],
                                                             'info': [m3, ]})

    def test_social_share(self):
        """
        Test social share tags with unicode input
        """
        t = Template('{% load spirit_tags %}'
                     '{% get_facebook_share_url url="/á/foo bar/" title="á" %}'
                     '{% get_twitter_share_url url="/á/foo bar/" title="á" %}'
                     '{% get_gplus_share_url url="/á/foo bar/" %}'
                     '{% get_email_share_url url="/á/foo bar/" title="á" %}'
                     '{% get_share_url url="/á/foo bar/" %}')
        res = t.render(Context({'request': RequestFactory().get('/'), }))
        self.assertEqual(res.strip(), "http://www.facebook.com/sharer.php?u=100&p%5Burl%5D=http%3A%2F%2Ftestserver"
                                      "%2F%25C3%25A1%2Ffoo%2520bar%2F&p%5Btitle%5D=%C3%A1"
                                      "https://twitter.com/share?url=http%3A%2F%2Ftestserver%2F%25C3%25A1%2F"
                                      "foo%2520bar%2F&text=%C3%A1"
                                      "https://plus.google.com/share?url=http%3A%2F%2Ftestserver%2F%25C3%25A1%2F"
                                      "foo%2520bar%2F"
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
        t = Template('{% load spirit_tags %}'
                     '{% get_twitter_share_url url="/foo/" title=long_title %}')
        res = t.render(Context({'request': RequestFactory().get('/'), 'long_title': long_title}))
        url = urlunquote(res.strip())
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
        field = NestedModelChoiceField(queryset=Category.objects.all(),
                                       related_name='category_set',
                                       parent_field='parent_id',
                                       label_field='title')
        self.assertSequenceEqual(list(field.choices), [('', '---------'),
                                                       (3, '%s' % category.title),
                                                       (5, '--- %s' % subcategory.title),
                                                       (4, '%s' % category2.title)])


class UtilsTimezoneTests(TestCase):

    def test_timezone(self):
        """
        Timezones, requires pytz
        """
        for tz, text in TIMEZONE_CHOICES:
            timezone.activate(tz)

        self.assertRaises(Exception, timezone.activate, "badtimezone")


class UtilsDecoratorsTests(TestCase):

    def setUp(self):
        cache.clear()
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


class UtilsUserTests(TestCase):

    def setUp(self):
        cache.clear()
        self.user = test_utils.create_user()

    def test_user_activation_token_generator(self):
        """
        Validate if user can be activated
        """
        self.user.st.is_verified = False

        activation_token = UserActivationTokenGenerator()
        token = activation_token.generate(self.user)
        self.assertTrue(activation_token.is_valid(self.user, token))
        self.assertFalse(activation_token.is_valid(self.user, "bad token"))

        # Invalid after verification
        self.user.st.is_verified = True
        self.assertFalse(activation_token.is_valid(self.user, token))

        # Invalid for different user
        user2 = test_utils.create_user()
        self.assertFalse(activation_token.is_valid(user2, token))

    def test_user_email_change_token_generator(self):
        """
        Email change
        """
        new_email = "footoken@bar.com"
        email_change_token = UserEmailChangeTokenGenerator()
        token = email_change_token.generate(self.user, new_email)
        self.assertTrue(email_change_token.is_valid(self.user, token))
        self.assertFalse(email_change_token.is_valid(self.user, "bad token"))

        # get new email
        self.assertTrue(email_change_token.is_valid(self.user, token))
        self.assertEqual(email_change_token.get_email(), new_email)

        # Invalid for different user
        user2 = test_utils.create_user()
        self.assertFalse(email_change_token.is_valid(user2, token))

        # Invalid after email change
        self.user.email = "email_changed@bar.com"
        self.assertFalse(email_change_token.is_valid(self.user, token))

    def test_user_activation_email(self):
        """
        Send activation email
        """
        self._monkey_sender_called = False

        def monkey_sender(request, subject, template_name, context, email):
            self.assertEqual(request, req)
            self.assertEqual(email, [self.user.email, ])

            activation_token = UserActivationTokenGenerator()
            token = activation_token.generate(self.user)
            self.assertDictEqual(context, {'token': token, 'user_id': self.user.pk})

            self.assertEqual(subject, _("User activation"))
            self.assertEqual(template_name, 'spirit/user/activation_email.html')

            self._monkey_sender_called = True

        req = RequestFactory().get('/')

        org_sender, email.sender = email.sender, monkey_sender
        try:
            send_activation_email(req, self.user)
            self.assertTrue(self._monkey_sender_called)
        finally:
            email.sender = org_sender

    def test_user_activation_email_complete(self):
        """
        Integration test
        """
        req = RequestFactory().get('/')
        send_activation_email(req, self.user)
        self.assertEquals(len(mail.outbox), 1)

    def test_email_change_email(self):
        """
        Send change email
        """
        self._monkey_sender_called = False

        def monkey_sender(request, subject, template_name, context, email):
            self.assertEqual(request, req)
            self.assertEqual(email, [self.user.email, ])

            change_token = UserEmailChangeTokenGenerator()
            token = change_token.generate(self.user, new_email)
            self.assertDictEqual(context, {'token': token, })

            self.assertEqual(subject, _("Email change"))
            self.assertEqual(template_name, 'spirit/user/email_change_email.html')

            self._monkey_sender_called = True

        req = RequestFactory().get('/')
        new_email = "newfoobar@bar.com"

        org_sender, email.sender = email.sender, monkey_sender
        try:
            send_email_change_email(req, self.user, new_email)
            self.assertTrue(self._monkey_sender_called)
        finally:
            email.sender = org_sender

    def test_email_change_email_complete(self):
        """
        Integration test
        """
        req = RequestFactory().get('/')
        send_email_change_email(req, self.user, "foo@bar.com")
        self.assertEquals(len(mail.outbox), 1)

    def test_sender(self):
        """
        Base email sender
        """
        class SiteMock:
            name = "foo"
            domain = "bar.com"

        def monkey_get_current_site(request):
            return SiteMock

        def monkey_render_to_string(template, data):
            self.assertEquals(template, template_name)
            self.assertDictEqual(data, {'user_id': self.user.pk,
                                        'token': token,
                                        'site_name': SiteMock.name,
                                        'domain': SiteMock.domain,
                                        'protocol': 'https' if req.is_secure() else 'http'})
            return "email body"

        req = RequestFactory().get('/')
        token = "token"
        subject = SiteMock.name
        template_name = "template.html"
        context = {'user_id': self.user.pk, 'token': token}

        org_site, email.get_current_site = email.get_current_site, monkey_get_current_site
        org_render_to_string, email.render_to_string = email.render_to_string, monkey_render_to_string
        try:
            sender(req, subject, template_name, context, [self.user.email, ])
        finally:
            email.get_current_site = org_site
            email.render_to_string = org_render_to_string

        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, SiteMock.name)
        self.assertEquals(mail.outbox[0].body, "email body")
        self.assertEquals(mail.outbox[0].from_email, "foo <noreply@bar.com>")
        self.assertEquals(mail.outbox[0].to, [self.user.email, ])
