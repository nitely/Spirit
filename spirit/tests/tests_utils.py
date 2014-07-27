#-*- coding: utf-8 -*-

import datetime
import json
import os

from markdown import markdown
from markdown import Markdown

from django.core.cache import cache
from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.template import Template, Context, TemplateSyntaxError
from django import forms
from django.utils import translation
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpResponseRedirect
from django.http import Http404, HttpResponse
from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.timezone import utc
from django.utils.http import urlunquote

from spirit.models.category import Category
from spirit.utils.forms import NestedModelChoiceField
from spirit.utils.timezone import TIMEZONE_CHOICES
from spirit.utils.decorators import moderator_required, administrator_required
from spirit.utils.user.tokens import UserActivationTokenGenerator, UserEmailChangeTokenGenerator
from spirit.utils.user.email import send_activation_email, send_email_change_email, sender
from spirit.utils.user import email

from spirit import utils as spirit_utils
from spirit.templatetags.tags.utils import time as ttags_utils
import utils as test_utils
from spirit.utils.markdown import quotify
from spirit.templatetags.tags.utils.messages import render_messages


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

        res = spirit_utils.render_form_errors(MockForm())
        lines = [line.strip() for line in res.splitlines()]
        self.assertEqual("".join(lines), '<ul class="errorlist"><li>error1</li><li>error2</li><li>error3</li></ul>')

    def test_json_response(self):
        """
        return json_response
        """
        res = spirit_utils.json_response()
        self.assertIsInstance(res, HttpResponse)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/json')
        self.assertDictEqual(json.loads(res.content), {})

        res = spirit_utils.json_response({"foo": "bar", })
        self.assertDictEqual(json.loads(res.content), {"foo": "bar", })

        res = spirit_utils.json_response(status=404)
        self.assertEqual(res.status_code, 404)

    def test_mkdir_p(self):
        """
        mkdir -p
        """
        # Empty path should raise an exception
        self.assertRaises(OSError, spirit_utils.mkdir_p, "")

        # Try to create an existing dir should do nothing
        self.assertTrue(os.path.isdir(settings.BASE_DIR))
        spirit_utils.mkdir_p(settings.BASE_DIR)

        # Create path tree
        # setup
        path = os.path.join(settings.BASE_DIR, "test_foo")
        sub_path = os.path.join(path, "bar")
        self.assertFalse(os.path.isdir(sub_path))
        self.assertFalse(os.path.isdir(path))
        # test
        spirit_utils.mkdir_p(sub_path)
        self.assertTrue(os.path.isdir(sub_path))
        # clean up
        os.rmdir(sub_path)
        os.rmdir(path)


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
        t = Template(u'{% load spirit_tags %}'
                     u'{% get_facebook_share_url url="/á/foo bar/" title="á" %}'
                     u'{% get_twitter_share_url url="/á/foo bar/" title="á" %}'
                     u'{% get_gplus_share_url url="/á/foo bar/" %}'
                     u'{% get_email_share_url url="/á/foo bar/" title="á" %}'
                     u'{% get_share_url url="/á/foo bar/" %}')
        res = t.render(Context({'request': RequestFactory().get('/'), }))
        self.assertEqual(res.strip(), u"http://www.facebook.com/sharer.php?u=100&p%5Burl%5D=http%3A%2F%2Ftestserver"
                                      u"%2F%25C3%25A1%2Ffoo%2520bar%2F&p%5Btitle%5D=%C3%A1"
                                      u"https://twitter.com/share?url=http%3A%2F%2Ftestserver%2F%25C3%25A1%2F"
                                      u"foo%2520bar%2F&text=%C3%A1"
                                      u"https://plus.google.com/share?url=http%3A%2F%2Ftestserver%2F%25C3%25A1%2F"
                                      u"foo%2520bar%2F"
                                      u"mailto:?body=http%3A%2F%2Ftestserver%2F%25C3%25A1%2Ffoo%2520bar%2F"
                                      u"&subject=%C3%A1&to="
                                      u"http://testserver/%C3%A1/foo%20bar/")

    def test_social_share_twitter_length(self):
        """
        Twitter allows up to 140 chars, takes 23 for urls (https)
        """
        long_title = u"á" * 150
        t = Template(u'{% load spirit_tags %}'
                     u'{% get_twitter_share_url url="/foo/" title=long_title %}')
        res = t.render(Context({'request': RequestFactory().get('/'), 'long_title': long_title}))
        url = urlunquote(res.strip())
        self.assertEqual(len(url.split("text=")[-1]) + 23, 139)


class UtilsFormsTests(TestCase):

    def test_nested_model_choise_form(self):
        """
        NestedModelChoiceField
        """
        category = test_utils.create_category()
        category2 = test_utils.create_category()
        subcategory = test_utils.create_subcategory(category)
        field = NestedModelChoiceField(queryset=Category.objects.all(),
                                       related_name='category_set',
                                       parent_field='parent_id',
                                       label_field='title')
        self.assertSequenceEqual(list(field.choices), [('', u'---------'),
                                                       (1, u'%s' % category.title),
                                                       (3, u'--- %s' % subcategory.title),
                                                       (2, u'%s' % category2.title)])


class UtilsTimezoneTests(TestCase):

    def test_timezone(self):
        """
        Timezones, requires pytz
        """
        for tz, text in TIMEZONE_CHOICES:
            timezone.activate(tz)

        self.assertRaises(Exception, timezone.activate, "badtimezone")


class UtilsDecoratorsTests(TestCase):

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

        req.user = User()
        req.user.is_moderator = False
        self.assertRaises(PermissionDenied, view, req)

        req.user.is_moderator = True
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

        req.user = User()
        req.user.is_administrator = False
        self.assertRaises(PermissionDenied, view, req)

        req.user.is_administrator = True
        self.assertIsNone(view(req))


class UtilsMarkdownTests(TestCase):

    def setUp(self):
        cache.clear()
        self.user = test_utils.create_user(username="nitely", slug="nitely")
        self.user2 = test_utils.create_user(username="esteban")
        self.user3 = test_utils.create_user(username=u"áéíóú")

    def test_markdown_mentions(self):
        """
        markdown mentions
        """
        comment = u"@nitely, @esteban,@áéíóú, @fakeone"
        comment_md = markdown(comment,
                              output_formats='html5',
                              safe_mode='escape',
                              extensions=['spirit.utils.markdown.mention', ])
        self.assertEqual(comment_md, u'<p><a href="%s">@nitely</a>, '
                                     u'<a href="%s">@esteban</a>,'
                                     u'<a href="%s">@\xe1\xe9\xed\xf3\xfa</a>, '
                                     u'@fakeone</p>' %
                                     (self.user.get_absolute_url(),
                                      self.user2.get_absolute_url(),
                                      self.user3.get_absolute_url()))

    @override_settings(ST_MENTIONS_PER_COMMENT=2)
    def test_markdown_mentions_limit(self):
        """
        markdown mentions limit
        """
        comment = u"@a, @b, @nitely"
        comment_md = markdown(comment,
                              output_formats='html5',
                              safe_mode='escape',
                              extensions=['spirit.utils.markdown.mention', ])
        self.assertEqual(comment_md, u"<p>@a, @b, @nitely</p>")

    def test_markdown_mentions_dict(self):
        """
        markdown mentions dict
        """
        comment = u"@nitely, @esteban"
        md = Markdown(output_formats='html5',
                      safe_mode='escape',
                      extensions=['spirit.utils.markdown.mention', ])
        comment_md = md.convert(comment)
        # mentions get dianmically added on MentionifyExtension
        self.assertDictEqual(md.mentions, {'nitely': self.user,
                                           'esteban': self.user2})

    def test_markdown_emoji(self):
        """
        markdown emojify
        """
        comment = u":airplane:, :8ball: :bademoji: foo:"
        comment_md = markdown(comment,
                              output_formats='html5',
                              safe_mode='escape',
                              extensions=['spirit.utils.markdown.emoji', ])
        self.assertEqual(comment_md, u'<p><img alt="airplane" src="%(static)sspirit/emojis/airplane.png" />, '
                                     u'<img alt="8ball" src="%(static)sspirit/emojis/8ball.png" /> '
                                     u':bademoji: foo:</p>' % {'static': settings.STATIC_URL, })

    def test_markdown_quote(self):
        """
        markdown quote
        """
        comment = u"text\nnew line"
        quote = quotify(comment, self.user)
        self.assertListEqual(quote.splitlines(), (u"@%s\n> text\n> new line\n\n" % self.user.username).splitlines())

    def test_markdown_image(self):
        """
        markdown image
        """
        comment = u"http://foo.bar/image.png\nhttp://www.foo.bar.fb/path/image.png\n" \
                  u"https://foo.bar/image.png\n" \
                  u"bad http://foo.bar/image.png\nhttp://foo.bar/image.png bad\nhttp://bad.png\n" \
                  u"http://foo.bar/.png\n![im](http://foo.bar/not_imagified.png)\n" \
                  u"foo.bar/bad.png\nhttp://foo.bar/<escaped>.png"
        comment_md = markdown(comment,
                              output_formats='html5',
                              safe_mode='escape',
                              extensions=['spirit.utils.markdown.image', ])
        self.assertListEqual(comment_md.splitlines(), u'<p><img alt="image" src="http://foo.bar/image.png" />'
                                                  u'\n<img alt="image" src="http://www.foo.bar.fb/path/image.png" />'
                                                  u'\n<img alt="image" src="https://foo.bar/image.png" />'
                                                  u'\nbad http://foo.bar/image.png'
                                                  u'\nhttp://foo.bar/image.png bad'
                                                  u'\nhttp://bad.png'
                                                  u'\nhttp://foo.bar/.png'
                                                  u'\n<img alt="im" src="http://foo.bar/not_imagified.png" />'
                                                  u'\nfoo.bar/bad.png'
                                                  u'\n<img alt="image" src="http://foo.bar/&lt;escaped&gt;.png" /></p>'.splitlines())

    def test_markdown_youtube(self):
        """
        markdown youtube
        """
        comment = u"https://www.youtube.com/watch?v=Z0UISCEe52Y\n" \
                  u"http://youtu.be/afyK1HSFfgw\n" \
                  u"https://www.youtube.com/embed/vsF0K3Ou1v0\n" \
                  u"https://www.youtube.com/watch?v=<bad>\n" \
                  u"https://www.noyoutube.com/watch?v=Z0UISCEe52Y\n" \
                  u"badbad https://www.youtube.com/watch?v=Z0UISCEe52Y\n" \
                  u"https://www.youtube.com/watch?v=Z0UISCEe52Y badbad\n"
        comment_md = markdown(comment,
                              output_formats='html5',
                              safe_mode='escape',
                              extensions=['spirit.utils.markdown.youtube', ])
        self.assertListEqual(comment_md.splitlines(), u'<p><span class="video"><iframe src="https://www.youtube.com/embed/Z0UISCEe52Y?feature=oembed" allowfullscreen></iframe></span>'
                                                  u'\n<span class="video"><iframe src="https://www.youtube.com/embed/afyK1HSFfgw?feature=oembed" allowfullscreen></iframe></span>'
                                                  u'\n<span class="video"><iframe src="https://www.youtube.com/embed/vsF0K3Ou1v0?feature=oembed" allowfullscreen></iframe></span>'
                                                  u'\nhttps://www.youtube.com/watch?v=&lt;bad&gt;'
                                                  u'\nhttps://www.noyoutube.com/watch?v=Z0UISCEe52Y'
                                                  u'\nbadbad https://www.youtube.com/watch?v=Z0UISCEe52Y'
                                                  u'\nhttps://www.youtube.com/watch?v=Z0UISCEe52Y badbad</p>'.splitlines())

    def test_markdown_vimeo(self):
        """
        markdown vimeo
        """
        self.maxDiff = None
        comment = u"https://vimeo.com/11111111\n" \
                  u"https://www.vimeo.com/11111111\n" \
                  u"https://player.vimeo.com/video/11111111\n" \
                  u"https://vimeo.com/channels/11111111\n" \
                  u"https://vimeo.com/groups/name/videos/11111111\n" \
                  u"https://vimeo.com/album/2222222/video/11111111\n" \
                  u"https://vimeo.com/11111111?param=value\n" \
                  u"https://novimeo.com/11111111\n" \
                  u"bad https://novimeo.com/11111111\n" \
                  u"https://novimeo.com/11111111 bad"
        comment_md = markdown(comment,
                              output_formats='html5',
                              safe_mode='escape',
                              extensions=['spirit.utils.markdown.vimeo', ])
        self.assertListEqual(comment_md.splitlines(), u'<p><span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                                                  u'\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                                                  u'\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                                                  u'\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                                                  u'\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                                                  u'\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                                                  u'\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                                                  u'\nhttps://novimeo.com/11111111'
                                                  u'\nbad https://novimeo.com/11111111'
                                                  u'\nhttps://novimeo.com/11111111 bad</p>'.splitlines())

    def test_markdown_video(self):
        """
        markdown video
        """
        comment = u"http://foo.bar/video.mp4\nhttp://foo.bar/<escaped>.mp4"
        comment_md = markdown(comment,
                              output_formats='html5',
                              safe_mode='escape',
                              extensions=['spirit.utils.markdown.video', ])
        self.assertListEqual(comment_md.splitlines(), u'<p><video controls><source src="http://foo.bar/video.mp4">'
                                                      u'<a href="http://foo.bar/video.mp4">http://foo.bar/video.mp4</a></video>'
                                                      u'\n<video controls><source src="http://foo.bar/&lt;escaped&gt;.mp4">'
                                                      u'<a href="http://foo.bar/&lt;escaped&gt;.mp4">'
                                                      u'http://foo.bar/&lt;escaped&gt;.mp4</a></video></p>'.splitlines())

    def test_markdown_audio(self):
        """
        markdown audio
        """
        self.maxDiff = None
        comment = u"http://foo.bar/audio.mp3\nhttp://foo.bar/<escaped>.mp3"
        comment_md = markdown(comment,
                              output_formats='html5',
                              safe_mode='escape',
                              extensions=['spirit.utils.markdown.audio', ])
        self.assertListEqual(comment_md.splitlines(), u'<p><audio controls><source src="http://foo.bar/audio.mp3"><a href="http://foo.bar/audio.mp3">http://foo.bar/audio.mp3</a></audio>'
                                                  u'\n<audio controls><source src="http://foo.bar/&lt;escaped&gt;.mp3"><a href="http://foo.bar/&lt;escaped&gt;.mp3">http://foo.bar/&lt;escaped&gt;.mp3</a></audio></p>'.splitlines())


class UtilsUserTests(TestCase):

    def setUp(self):
        cache.clear()
        self.user = test_utils.create_user()

    def test_user_activation_token_generator(self):
        """
        Validate if user can be activated
        """
        self.user.last_login = self.user.last_login - datetime.timedelta(hours=1)

        activation_token = UserActivationTokenGenerator()
        token = activation_token.generate(self.user)
        self.assertTrue(activation_token.is_valid(self.user, token))
        self.assertFalse(activation_token.is_valid(self.user, "bad token"))

        # Invalid for different user
        user2 = test_utils.create_user()
        self.assertFalse(activation_token.is_valid(user2, token))

        # Invalid after login
        test_utils.login(self)
        user = test_utils.User.objects.get(pk=self.user.pk)
        self.assertFalse(activation_token.is_valid(user, token))

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