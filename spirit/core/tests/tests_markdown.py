# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.test.utils import override_settings
from django.utils import translation
from django.utils import timezone

from . import utils
from ..utils.markdown import Markdown, quotify


now_fixed = timezone.now()


class UtilsMarkdownTests(TestCase):

    def setUp(self):
        utils.cache_clear()
        self.user = utils.create_user(username="nitely")
        self.user2 = utils.create_user(username="esteban")
        self.user3 = utils.create_user(username="áéíóú")

    def test_markdown_escape(self):
        """
        Should escape html
        """
        comment = "<span>foo</span>"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, '<p>&lt;span&gt;foo&lt;/span&gt;</p>')

    def test_markdown_html(self):
        """
        Should escape html
        """
        # todo: fixed on mistune 0.7.2 ?
        # markdown is not parsed within html tags, there is a way to parse it
        # but it's broken since it gets escaped afterwards.
        comment = (
            "<div>\n"
            "<em>*foo*</em>\n"
            "<em>*bar*</em>\n"
            "*foobar*\n"
            "@nitely\n"
            "*<em>foobar</em>*\n"
            "</div>\n"
            "<em>*foo*</em>\n"
            "<em>@nitely</em>\n"  # Why this gets parsed properly is beyond me
            "*<em>foobar</em>*\n"
        )
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, (
            '<p>&lt;div&gt;\n'
            '&lt;em&gt;*foo*&lt;/em&gt;\n'
            '&lt;em&gt;*bar*&lt;/em&gt;\n'
            '*foobar*\n'
            '@nitely\n'
            '*&lt;em&gt;foobar&lt;/em&gt;*\n'
            '&lt;/div&gt;<br>\n'
            '&lt;em&gt;*foo*&lt;/em&gt;<br>\n'
            '&lt;em&gt;<a class="comment-mention" rel="nofollow" href="%s">@nitely</a>&lt;/em&gt;<br>\n'
            '<em>&lt;em&gt;foobar&lt;/em&gt;</em></p>'
        ) % (self.user.st.get_absolute_url(), ))

    def test_markdown_mentions(self):
        """
        markdown mentions
        """
        comment = "@nitely, @esteban,@áéíóú, @fakeone"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md,
            '<p><a class="comment-mention" rel="nofollow" href="%s">@nitely</a>, '
            '<a class="comment-mention" rel="nofollow" href="%s">@esteban</a>,'
            '<a class="comment-mention" rel="nofollow" href="%s">@áéíóú</a>, '
            '@fakeone</p>' %
            (self.user.st.get_absolute_url(),
             self.user2.st.get_absolute_url(),
             self.user3.st.get_absolute_url()))

    @override_settings(ST_MENTIONS_PER_COMMENT=2)
    def test_markdown_mentions_limit(self):
        """
        markdown mentions limit
        """
        comment = "@a, @b, @nitely"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, "<p>@a, @b, @nitely</p>")

    def test_markdown_mentions_dict(self):
        """
        markdown mentions dict
        """
        comment = "@nitely, @esteban"
        md = Markdown()
        md.render(comment)
        # mentions get dynamically added on MentionifyExtension
        self.assertDictEqual(md.get_mentions(), {
            'nitely': self.user,
            'esteban': self.user2})

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=True)
    def test_markdown_mentions_dict_ci(self):
        """
        markdown mentions dict case-insensitive
        """
        comment = "@NiTely, @EsTebaN, @nitEly, @NiteLy"
        md = Markdown()
        md.render(comment)
        self.assertDictEqual(md.get_mentions(), {
            'nitely': self.user,
            'esteban': self.user2})

    @override_settings(ST_CASE_INSENSITIVE_USERNAMES=False)
    def test_markdown_mentions_dict_ci_off(self):
        comment = "@NiTely, @esteban, @nitEly, @NiteLy"
        md = Markdown()
        md.render(comment)
        self.assertDictEqual(md.get_mentions(), {
            'esteban': self.user2})

    def test_markdown_emoji(self):
        """
        markdown emojify
        """
        comment = ":airplane:, :8ball: :+1: :bademoji: foo:"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, '<p><i class="tw tw-airplane" title=":airplane:"></i>, '
                                     '<i class="tw tw-8ball" title=":8ball:"></i> '
                                     '<i class="tw tw-plus1" title=":+1:"></i> '
                                     ':bademoji: foo:</p>')

    @override_settings(LANGUAGE_CODE='en')
    def test_markdown_quote(self):
        """
        markdown quote
        """
        comment = "text\nnew line"
        quote = quotify(comment, self.user)
        self.assertListEqual(
            quote.splitlines(),
            ("> @%s said:\n> text\n> new line\n\n" % self.user.st.nickname).splitlines())

    @override_settings(LANGUAGE_CODE='en')
    def test_markdown_quote_header_language(self):
        """
        markdown quote
        "@user said:" should keep the default language (settings.LANGUAGE_CODE)
        """
        comment = ""
        quote = quotify(comment, self.user)

        with translation.override('es'):
            self.assertListEqual(
                quote.splitlines(),
                ("> @%s said:\n> \n\n" % self.user.st.nickname).splitlines())

    @override_settings(LANGUAGE_CODE='en')
    def test_markdown_quote_no_polls(self):
        """
        should remove poll markdown
        """
        comment = "foo\n" \
                  "[poll param=value]\n" \
                  "1. [/fake_closing_tag]\n" \
                  "2. opt 2\n" \
                  "[/poll]\n" \
                  "bar\n" \
                  "[poll param=value]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        quote = quotify(comment, self.user)
        self.assertListEqual(
            quote.splitlines(),
            ("> @%s said:\n> foo\n> \n> bar\n\n" % self.user.username).splitlines())

    def test_markdown_image(self):
        """
        markdown image
        """
        comment = (
            "http://foo.bar/image.png\n"
            "http://www.foo.bar.fb/path/image.png\n"
            "https://foo.bar/image.png\n"
            "bad http://foo.bar/image.png\n"
            "http://foo.bar/image.png bad\nhttp://bad.png\n"
            "http://foo.bar/.png\n"
            "![im](http://foo.bar/not_imagified.png)\n"
            "foo.bar/bad.png\n\n"
            "http://foo.bar/<escaped>.png"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<p><img src="http://foo.bar/image.png" alt="image" title="image"></p>',
                '<p><img src="http://www.foo.bar.fb/path/image.png" alt="image" title="image"></p>',
                '<p><img src="https://foo.bar/image.png" alt="image" title="image"></p>',

                # auto-link
                '<p>bad <a rel="nofollow" href="http://foo.bar/image.png">http://foo.bar/image.png</a><br>',
                '<a rel="nofollow" href="http://foo.bar/image.png">http://foo.bar/image.png</a> bad<br>',
                '<a rel="nofollow" href="http://bad.png">http://bad.png</a><br>',
                '<a rel="nofollow" href="http://foo.bar/.png">http://foo.bar/.png</a><br>',
                '<img src="http://foo.bar/not_imagified.png" alt="im"><br>',
                'foo.bar/bad.png</p>',

                '<p><img src="http://foo.bar/&lt;escaped&gt;.png" alt="&lt;escaped&gt;" title="&lt;escaped&gt;"></p>'
            ]
        )

    def test_markdown_youtube(self):
        """
        markdown youtube
        """
        comment = (
            "https://www.youtube.com/watch?v=Z0UISCEe52Y\n"
            "https://www.youtube.com/watch?v=Z0UISCEe52Y&t=1m13s\n"
            "https://www.youtube.com/watch?v=O1QQajfobPw&t=1h1m38s\n"
            "https://www.youtube.com/watch?v=O1QQajfobPw&t=105m\n"
            "https://www.youtube.com/watch?v=O1QQajfobPw&feature=youtu.be&t=3698\n"
            "http://youtu.be/afyK1HSFfgw\n"
            "http://youtu.be/O1QQajfobPw?t=1h1m38s\n"
            "https://www.youtube.com/embed/vsF0K3Ou1v0\n"
            "https://www.youtube.com/watch?v=<bad>\n"
            "https://www.noyoutube.com/watch?v=Z0UISCEe52Y\n"
            "badbad https://www.youtube.com/watch?v=Z0UISCEe52Y\n\n"
            "https://www.youtube.com/watch?v=Z0UISCEe52Y badbad\n"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<span class="video"><iframe src="https://www.youtube.com/embed/Z0UISCEe52Y?html5=1" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/Z0UISCEe52Y?html5=1&start=73" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/O1QQajfobPw?html5=1&start=3698" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/O1QQajfobPw?html5=1&start=6300" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/O1QQajfobPw?html5=1&start=3698" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/afyK1HSFfgw?html5=1"'
                ' allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/O1QQajfobPw?html5=1&start=3698" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://www.youtube.com/embed/vsF0K3Ou1v0?html5=1"'
                ' allowfullscreen></iframe></span>',
                '<p><a rel="nofollow" href="https://www.youtube.com/watch?v=&lt;bad&gt;">'
                'https://www.youtube.com/watch?v=&lt;bad&gt;</a></p>',
                '<p><a rel="nofollow" href="https://www.noyoutube.com/watch?v=Z0UISCEe52Y">'
                'https://www.noyoutube.com/watch?v=Z0UISCEe52Y</a></p>',
                '<p>badbad <a rel="nofollow" href="https://www.youtube.com/watch?v=Z0UISCEe52Y">'
                'https://www.youtube.com/watch?v=Z0UISCEe52Y</a></p>',
                '<p><a rel="nofollow" href="https://www.youtube.com/watch?v=Z0UISCEe52Y">'
                'https://www.youtube.com/watch?v=Z0UISCEe52Y</a> badbad</p>'
            ]
        )

    def test_markdown_vimeo(self):
        """
        markdown vimeo
        """
        comment = (
            "https://vimeo.com/11111111\n"
            "https://www.vimeo.com/11111111\n"
            "https://player.vimeo.com/video/11111111\n"
            "https://vimeo.com/channels/11111111\n"
            "https://vimeo.com/groups/name/videos/11111111\n"
            "https://vimeo.com/album/2222222/video/11111111\n"
            "https://vimeo.com/11111111?param=value\n"
            "https://novimeo.com/11111111\n"
            "bad https://novimeo.com/11111111\n\n"
            "https://novimeo.com/11111111 bad"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" '
                'allowfullscreen></iframe></span>',

                '<p><a rel="nofollow" href="https://novimeo.com/11111111">https://novimeo.com/11111111</a></p>',
                '<p>bad <a rel="nofollow" href="https://novimeo.com/11111111">https://novimeo.com/11111111</a></p>',
                '<p><a rel="nofollow" href="https://novimeo.com/11111111">https://novimeo.com/11111111</a> bad</p>'
            ]
        )

    def test_markdown_gfycat(self):
        """
        markdown vimeo
        """
        comment = (
            "https://gfycat.com/PointedVengefulHyracotherium\n"
            "https://www.gfycat.com/PointedVengefulHyracotherium\n"
            "http://gfycat.com/PointedVengefulHyracotherium\n"
            "http://www.gfycat.com/PointedVengefulHyracotherium\n"
            "bad https://gfycat.com/PointedVengefulHyracotherium\n"
            "https://gfycat.com/PointedVengefulHyracotherium bad"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<span class="video"><iframe src="https://gfycat.com/ifr/PointedVengefulHyracotherium" '
                'frameborder="0" scrolling="no" allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://gfycat.com/ifr/PointedVengefulHyracotherium" '
                'frameborder="0" scrolling="no" allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://gfycat.com/ifr/PointedVengefulHyracotherium" '
                'frameborder="0" scrolling="no" allowfullscreen></iframe></span>',
                '<span class="video"><iframe src="https://gfycat.com/ifr/PointedVengefulHyracotherium" '
                'frameborder="0" scrolling="no" allowfullscreen></iframe></span>',

                '<p>bad <a rel="nofollow" href="https://gfycat.com/PointedVengefulHyracotherium">'
                'https://gfycat.com/PointedVengefulHyracotherium</a><br>',
                '<a rel="nofollow" href="https://gfycat.com/PointedVengefulHyracotherium">'
                'https://gfycat.com/PointedVengefulHyracotherium</a> bad</p>'
            ]
        )

    def test_markdown_video(self):
        """
        markdown video
        """
        comment = (
            "http://foo.bar/video.mp4\n"
            "http://foo.bar/<escaped>.mp4"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<video controls><source src="http://foo.bar/video.mp4">'
                '<a rel="nofollow" href="http://foo.bar/video.mp4">http://foo.bar/video.mp4</a></video>',
                '<video controls><source src="http://foo.bar/&lt;escaped&gt;.mp4">'
                '<a rel="nofollow" href="http://foo.bar/&lt;escaped&gt;.mp4">'
                'http://foo.bar/&lt;escaped&gt;.mp4</a></video>'
            ]
        )

    def test_markdown_audio(self):
        """
        markdown audio
        """
        comment = (
            "http://foo.bar/audio.mp3\n"
            "http://foo.bar/<escaped>.mp3"
        )
        comment_md = Markdown().render(comment)
        self.assertListEqual(
            comment_md.splitlines(),
            [
                '<audio controls><source src="http://foo.bar/audio.mp3"><a '
                'rel="nofollow" href="http://foo.bar/audio.mp3">http://foo.bar/audio.mp3</a></audio>',
                '<audio controls><source src="http://foo.bar/&lt;escaped&gt;.mp3"><a '
                'rel="nofollow" href="http://foo.bar/&lt;escaped&gt;.mp3">'
                'http://foo.bar/&lt;escaped&gt;.mp3</a></audio>'
            ]
        )

    def test_markdown_poll(self):
        """
        markdown poll
        """
        comment = "[poll name=foo_1]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "3. opt 3\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<poll name=foo_1>')
        self.assertEqual(md.get_polls(), {
            'polls': [
                {'name': 'foo_1', }
            ],
            'choices': [
                {'number': 1, 'description': 'opt 1', 'poll_name': 'foo_1'},
                {'number': 2, 'description': 'opt 2', 'poll_name': 'foo_1'},
                {'number': 3, 'description': 'opt 3', 'poll_name': 'foo_1'}
            ]
        })

    def test_markdown_poll_params(self):
        """
        Should accept min, max, close, and title
        """
        def mock_now():
            return now_fixed

        org_now, timezone.now = timezone.now, mock_now
        try:
            comment = "[poll name=foo_1 min=1 max=2 close=1d mode=default]\n" \
                      "# Foo or bar?\n" \
                      "1. opt 1\n" \
                      "2. opt 2\n" \
                      "[/poll]"
            md = Markdown()
            comment_md = md.render(comment)
            self.assertEqual(comment_md, '<poll name=foo_1>')
            self.assertEqual(md.get_polls(), {
                'polls': [
                    {
                        'name': 'foo_1',
                        'choice_min': 1,
                        'choice_max': 2,
                        'title': 'Foo or bar?',
                        'mode': 0,
                        'close_at': now_fixed + timezone.timedelta(days=1)
                    }
                ],
                'choices': [
                    {'number': 1, 'description': 'opt 1', 'poll_name': 'foo_1'},
                    {'number': 2, 'description': 'opt 2', 'poll_name': 'foo_1'}
                ]
            })
        finally:
            timezone.now = org_now

    def test_markdown_poll_invalid_one_option(self):
        """
        Should have at least two options
        """
        comment = "[poll name=foo_1]\n" \
                  "1. opt 1\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo_1]<br>1. opt 1<br>[/poll]</p>')
        self.assertEqual(md.get_polls(), {'polls': [], 'choices': []})

    def test_markdown_poll_invalid_no_options(self):
        """
        Should have at least two options
        """
        comment = "[poll name=foo_1]\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo_1]<br>[/poll]</p>')
        self.assertEqual(md.get_polls(), {'polls': [], 'choices': []})

    def test_markdown_poll_invalid_no_name(self):
        """
        Should have a name param
        """
        comment = "[poll]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll]<br>1. opt 1<br>2. opt 2<br>[/poll]</p>')
        self.assertEqual(md.get_polls(), {'polls': [], 'choices': []})

    def test_markdown_poll_and_text(self):
        """
        Should work with surrounding text
        """
        comment = "foo\n" \
                  "\n" \
                  "[poll name=foo_1]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]\n" \
                  "bar"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>foo</p>\n<poll name=foo_1>\n<p>bar</p>')

    def test_markdown_poll_many(self):
        """
        Should work with many polls in the same comment
        """
        comment = "[poll name=foo_1]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]\n" \
                  "\n" \
                  "[poll name=foo_2]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<poll name=foo_1>\n<poll name=foo_2>')
        polls = md.get_polls()
        self.assertEqual(len(polls['polls']), 2)

    def test_markdown_poll_truncates_name_title_description(self):
        """
        Should truncate name, title and description to model max_length
        """
        name = 'a' * 255 * 2
        title = 'b' * 255 * 2
        description = 'c' * 255 * 2
        comment = "[poll name=%(name)s]\n" \
                  "# %(title)s\n" \
                  "1. %(description)s\n" \
                  "2. %(description)s\n" \
                  "[/poll]" % {'name': name, 'title': title, 'description': description}
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<poll name=%s>' % name[:255])
        polls = md.get_polls()
        self.assertEqual(len(polls['polls'][0]['name']), 255)
        self.assertEqual(len(polls['polls'][0]['title']), 255)
        self.assertEqual(len(polls['choices'][0]['description']), 255)
        self.assertEqual(len(polls['choices'][0]['poll_name']), 255)
        self.assertEqual(len(polls['choices'][1]['description']), 255)
        self.assertEqual(len(polls['choices'][1]['poll_name']), 255)

    def test_markdown_poll_choice_description_escaped(self):
        """
        Should escape the choice description
        """
        comment = "[poll name=foo]\n" \
                  "1. <i'm bad>\n" \
                  "2. option\n" \
                  "[/poll]"
        md = Markdown()
        md.render(comment)
        polls = md.get_polls()
        self.assertEqual(polls['choices'][0]['description'], '&lt;i&#39;m bad&gt;')

    def test_markdown_poll_title_escaped(self):
        """
        Should escape the title
        """
        comment = "[poll name=foo]\n" \
                  "# <i'm bad>\n" \
                  "1. option1\n" \
                  "2. option2\n" \
                  "[/poll]"
        md = Markdown()
        md.render(comment)
        polls = md.get_polls()
        self.assertEqual(polls['polls'][0]['title'], '&lt;i&#39;m bad&gt;')

    def test_markdown_poll_choice_limit_ok(self):
        """
        Should not exceed the limit
        """
        limit = 20  # todo: change to setting
        opts = '\n'.join('%s. opt' % x for x in range(limit))
        comment = "[poll name=foo]\n" + opts + "\n[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<poll name=foo>')
        polls = md.get_polls()
        self.assertEqual(len(polls['choices']), limit)

    def test_markdown_poll_choice_limit_pre_exceeded(self):
        """
        Should not exceed the limit
        """
        limit = 20  # todo: change to setting
        comment = "[poll name=foo]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        polls = md.get_polls()
        polls['choices'].extend({} for _ in range(limit))
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo]<br>1. opt 1<br>2. opt 2<br>[/poll]</p>')
        polls = md.get_polls()
        self.assertEqual(len(polls['choices']), limit)

    def test_markdown_poll_choice_limit_exceeded(self):
        """
        Should not exceed the limit
        """
        limit = 20  # todo: change to setting
        opts = '\n'.join('%s. opt' % x for x in range(limit + 1))
        comment = "[poll name=foo]\n" + opts + "\n[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo]<br>' + opts.replace('\n', '<br>') + '<br>[/poll]</p>')
        polls = md.get_polls()
        self.assertEqual(len(polls['choices']), 0)

    def test_markdown_poll_unique_name(self):
        """
        Should not allow repeated names
        """
        comment = "[poll name=foo]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        polls = md.get_polls()
        polls['polls'].append({'name': 'foo'})
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo]<br>1. opt 1<br>2. opt 2<br>[/poll]</p>')
        polls = md.get_polls()
        self.assertEqual(len(polls['choices']), 0)
        self.assertEqual(len(polls['polls']), 1)

    def test_markdown_poll_unique_choice_numbers(self):
        """
        Should not allow repeated numbers
        """
        comment = "[poll name=foo]\n" \
                  "1. opt 1\n" \
                  "1. opt 2\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo]<br>1. opt 1<br>1. opt 2<br>2. opt 2<br>[/poll]</p>')
        polls = md.get_polls()
        self.assertEqual(len(polls['choices']), 0)
        self.assertEqual(len(polls['polls']), 0)

    def test_markdown_poll_unique_choice_coerced_numbers(self):
        """
        Should not allow repeated numbers (1 = 01 = 001)
        """
        comment = "[poll name=foo]\n" \
                  "1. opt 1\n" \
                  "01. opt 2\n" \
                  "001. opt 2\n" \
                  "2. opt 2\n" \
                  "02. opt 2\n" \
                  "002. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo]<br>'
                                     '1. opt 1<br>'
                                     '01. opt 2<br>'
                                     '001. opt 2<br>'
                                     '2. opt 2<br>'
                                     '02. opt 2<br>'
                                     '002. opt 2<br>'
                                     '[/poll]</p>')
        polls = md.get_polls()
        self.assertEqual(len(polls['choices']), 0)
        self.assertEqual(len(polls['polls']), 0)

    def test_markdown_poll_choice_min_le_than_max(self):
        """
        Should validate min is less or equal than max
        """
        comment = "[poll name=foo min=2 max=1]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo min=2 max=1]<br>1. opt 1<br>2. opt 2<br>[/poll]</p>')
        polls = md.get_polls()
        self.assertEqual(len(polls['choices']), 0)
        self.assertEqual(len(polls['polls']), 0)

    def test_markdown_poll_choice_min_greater_than_zero(self):
        """
        Should validate min is greater than 0
        """
        comment = "[poll name=foo min=0]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo min=0]<br>1. opt 1<br>2. opt 2<br>[/poll]</p>')
        polls = md.get_polls()
        self.assertEqual(len(polls['choices']), 0)
        self.assertEqual(len(polls['polls']), 0)

    def test_markdown_poll_choice_max_greater_than_zero(self):
        """
        Should validate max is greater than 0
        """
        comment = "[poll name=foo max=0]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo max=0]<br>1. opt 1<br>2. opt 2<br>[/poll]</p>')
        polls = md.get_polls()
        self.assertEqual(len(polls['choices']), 0)
        self.assertEqual(len(polls['polls']), 0)

    def test_markdown_poll_choice_max(self):
        """
        Should work with max only
        """
        comment = "[poll name=foo max=2]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "3. opt 3\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<poll name=foo>')
        polls = md.get_polls()
        self.assertEqual(polls['polls'][0]['choice_max'], 2)

    def test_markdown_poll_choice_min(self):
        """
        Should work with min only, max should default to choices length
        """
        comment = "[poll name=foo min=2]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "3. opt 3\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<poll name=foo>')
        polls = md.get_polls()
        self.assertEqual(polls['polls'][0]['choice_min'], 2)
        self.assertEqual(polls['polls'][0]['choice_max'], 3)

    def test_markdown_poll_truncates_close(self):
        """
        Should truncates the close days
        """
        def mock_now():
            return now_fixed

        org_now, timezone.now = timezone.now, mock_now
        try:
            comment = "[poll name=foo_1 close=100000000000d]\n" \
                      "# Foo or bar?\n" \
                      "1. opt 1\n" \
                      "2. opt 2\n" \
                      "[/poll]"
            md = Markdown()
            comment_md = md.render(comment)
            self.assertEqual(comment_md, '<poll name=foo_1>')
            self.assertEqual(
                md.get_polls()['polls'][0]['close_at'],
                now_fixed + timezone.timedelta(days=10000)
            )
        finally:
            timezone.now = org_now

    def test_markdown_poll_mode_default(self):
        """
        Should accept mode=default
        """
        comment = "[poll name=foo mode=default]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<poll name=foo>')
        polls = md.get_polls()
        self.assertEqual(polls['polls'][0]['mode'], 0)

    def test_markdown_poll_mode_secret(self):
        """
        Should accept mode=secret
        """
        comment = "[poll name=foo mode=secret]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<poll name=foo>')
        polls = md.get_polls()
        self.assertEqual(polls['polls'][0]['mode'], 1)

    def test_markdown_poll_mode_invalid(self):
        """
        Should not accept unknown mode
        """
        comment = "[poll name=foo mode=foo]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "[/poll]"
        md = Markdown()
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo mode=foo]<br>1. opt 1<br>2. opt 2<br>[/poll]</p>')

    def test_autolink(self):
        """
        Should parse the link as <a> tag
        """
        comment = "http://foo.com\n" \
                  "http://foo.com?foo=1&bar=2\n" \
                  "http://foo.com/<bad>"
        comment_md = Markdown().render(comment)
        self.assertEqual(
            comment_md.splitlines(),
            [
                '<p><a rel="nofollow" href="http://foo.com">http://foo.com</a></p>',
                '<p><a rel="nofollow" href="http://foo.com?foo=1&amp;bar=2">http://foo.com?foo=1&amp;bar=2</a></p>',
                '<p><a rel="nofollow" href="http://foo.com/&lt;bad&gt;">http://foo.com/&lt;bad&gt;</a></p>'
            ])

    def test_autolink_without_no_follow(self):
        """
        Should parse the link as <a> tag without no-follow
        """
        comment = "http://foo.com"
        comment_md = Markdown(no_follow=False).render(comment)
        self.assertEqual(comment_md, '<p><a href="http://foo.com">http://foo.com</a></p>')

    def test_link(self):
        """
        Should parse the link as <a> tag
        """
        comment = "[link](http://foo.com)"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, '<p><a rel="nofollow" href="http://foo.com">link</a></p>')

    def test_link_without_no_follow(self):
        """
        Should parse the link as <a> tag without no-follow
        """
        comment = "[link](http://foo.com)"
        comment_md = Markdown(no_follow=False).render(comment)
        self.assertEqual(comment_md, '<p><a href="http://foo.com">link</a></p>')

    def test_link_title(self):
        """
        Should parse the link as <a> tag
        """
        comment = "[link](http://foo.com \"bar\")"
        comment_md = Markdown().render(comment)
        self.assertEqual(comment_md, '<p><a rel="nofollow" href="http://foo.com" title="bar">link</a></p>')

    def test_link_title_without_no_follow(self):
        """
        Should parse the link as <a> tag without no-follow
        """
        comment = "[link](http://foo.com \"bar\")"
        comment_md = Markdown(no_follow=False).render(comment)
        self.assertEqual(comment_md, '<p><a href="http://foo.com" title="bar">link</a></p>')

    def test_link_safety(self):
        """
        Should sanitize the links to avoid XSS attacks
        """
        attack_vectors = (
            # "standard" javascript pseudo protocol
            ('javascript:alert`1`', ''),
            # bypass attempt
            ('jAvAsCrIpT:alert`1`', ''),
            # javascript pseudo protocol with entities
            ('javascript&colon;alert`1`', ''),
            # javascript pseudo protocol with prefix (dangerous in Chrome)
            ('\x1Ajavascript:alert`1`', ''),
            # data-URI (dangerous in Firefox)
            ('data:text/html,<script>alert`1`</script>', ''),
            # vbscript-URI (dangerous in Internet Explorer)
            ('vbscript:msgbox', ''),
            # breaking out of the attribute
            ('"<>', ''),
        )

        for vector, expected in attack_vectors:
            # Image
            self.assertEqual(
                Markdown().render('![atk](%s)' % vector),
                '<p><img src="%s" alt="atk"></p>' % expected)
            # Link
            self.assertEqual(
                Markdown().render('[atk](%s)' % vector),
                '<p><a rel="nofollow" href="%s">atk</a></p>' % expected)
