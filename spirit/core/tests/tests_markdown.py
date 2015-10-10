# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import translation
from django.conf import settings
from django.utils import timezone

from ..tests import utils as test_utils
from ..utils.markdown import Markdown, quotify


now_fixed = timezone.now()


class UtilsMarkdownTests(TestCase):

    def setUp(self):
        cache.clear()
        self.user = test_utils.create_user(username="nitely")
        self.user2 = test_utils.create_user(username="esteban")
        self.user3 = test_utils.create_user(username="áéíóú")

    def test_markdown_mentions(self):
        """
        markdown mentions
        """
        comment = "@nitely, @esteban,@áéíóú, @fakeone"
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p><a class="comment-mention" href="%s">@nitely</a>, '
                                     '<a class="comment-mention" href="%s">@esteban</a>,'
                                     '<a class="comment-mention" href="%s">@\xe1\xe9\xed\xf3\xfa</a>, '
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
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertEqual(comment_md, "<p>@a, @b, @nitely</p>")

    def test_markdown_mentions_dict(self):
        """
        markdown mentions dict
        """
        comment = "@nitely, @esteban"
        md = Markdown(escape=True, hard_wrap=True)
        md.render(comment)
        # mentions get dynamically added on MentionifyExtension
        self.assertDictEqual(md.get_mentions(), {'nitely': self.user,
                                                 'esteban': self.user2})

    def test_markdown_emoji(self):
        """
        markdown emojify
        """
        comment = ":airplane:, :8ball: :bademoji: foo:"
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p><img class="comment-emoji" src="%(static)sspirit/emojis/airplane.png">, '
                                     '<img class="comment-emoji" src="%(static)sspirit/emojis/8ball.png"> '
                                     ':bademoji: foo:</p>' % {'static': settings.STATIC_URL, })

    @override_settings(LANGUAGE_CODE='en')
    def test_markdown_quote(self):
        """
        markdown quote
        """
        comment = "text\nnew line"
        quote = quotify(comment, self.user)
        self.assertListEqual(quote.splitlines(), ("> @%s said:\n> text\n> new line\n\n" % self.user.username).splitlines())

    @override_settings(LANGUAGE_CODE='en')
    def test_markdown_quote_header_language(self):
        """
        markdown quote
        "@user said:" should keep the default language (settings.LANGUAGE_CODE)
        """
        comment = ""
        quote = quotify(comment, self.user)

        with translation.override('es'):
            self.assertListEqual(quote.splitlines(), ("> @%s said:\n> \n\n" % self.user.username).splitlines())

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
        self.assertListEqual(quote.splitlines(), ("> @%s said:\n> foo\n> \n> bar\n\n" % self.user.username).splitlines())

    def test_markdown_image(self):
        """
        markdown image
        """
        comment = "http://foo.bar/image.png\nhttp://www.foo.bar.fb/path/image.png\n" \
                  "https://foo.bar/image.png\n" \
                  "bad http://foo.bar/image.png\nhttp://foo.bar/image.png bad\nhttp://bad.png\n" \
                  "http://foo.bar/.png\n![im](http://foo.bar/not_imagified.png)\n" \
                  "foo.bar/bad.png\n\nhttp://foo.bar/<escaped>.png"
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertListEqual(comment_md.splitlines(), '<p><img src="http://foo.bar/image.png" alt="image" title="image"></p>\n'
                             '<p><img src="http://www.foo.bar.fb/path/image.png" alt="image" title="image"></p>\n'
                             '<p><img src="https://foo.bar/image.png" alt="image" title="image"></p>\n'
                             '<p>bad <a href="http://foo.bar/image.png">http://foo.bar/image.png</a><br>'  # autolink
                             '<a href="http://foo.bar/image.png">http://foo.bar/image.png</a> bad<br>'  # autolink
                             '<a href="http://bad.png">http://bad.png</a><br>'  # autolink
                             '<a href="http://foo.bar/.png">http://foo.bar/.png</a><br>'  # autolink
                             '<img src="http://foo.bar/not_imagified.png" alt="im"><br>'
                             'foo.bar/bad.png</p>\n'
                             '<p><img src="http://foo.bar/&lt;escaped&gt;.png" alt="&lt;escaped&gt;" title="&lt;escaped&gt;"></p>\n'.splitlines())

    def test_markdown_youtube(self):
        """
        markdown youtube
        """
        comment = "https://www.youtube.com/watch?v=Z0UISCEe52Y\n" \
                  "http://youtu.be/afyK1HSFfgw\n" \
                  "https://www.youtube.com/embed/vsF0K3Ou1v0\n" \
                  "https://www.youtube.com/watch?v=<bad>\n" \
                  "https://www.noyoutube.com/watch?v=Z0UISCEe52Y\n" \
                  "badbad https://www.youtube.com/watch?v=Z0UISCEe52Y\n" \
                  "https://www.youtube.com/watch?v=Z0UISCEe52Y badbad\n"
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertListEqual(comment_md.splitlines(), '<span class="video"><iframe src="https://www.youtube.com/embed/Z0UISCEe52Y?feature=oembed" allowfullscreen></iframe></span>'
                             '\n<span class="video"><iframe src="https://www.youtube.com/embed/afyK1HSFfgw?feature=oembed" allowfullscreen></iframe></span>'
                             '\n<span class="video"><iframe src="https://www.youtube.com/embed/vsF0K3Ou1v0?feature=oembed" allowfullscreen></iframe></span>'
                             '\n<p><a href="https://www.youtube.com/watch?v=&lt;bad&amp;gt">https://www.youtube.com/watch?v=&lt;bad&amp;gt</a>;<br>'  # smart_amp ain't smart
                             '<a href="https://www.noyoutube.com/watch?v=Z0UISCEe52Y">https://www.noyoutube.com/watch?v=Z0UISCEe52Y</a><br>'
                             'badbad <a href="https://www.youtube.com/watch?v=Z0UISCEe52Y">https://www.youtube.com/watch?v=Z0UISCEe52Y</a><br>'
                             '<a href="https://www.youtube.com/watch?v=Z0UISCEe52Y">https://www.youtube.com/watch?v=Z0UISCEe52Y</a> badbad</p>'.splitlines())

    def test_markdown_vimeo(self):
        """
        markdown vimeo
        """
        comment = "https://vimeo.com/11111111\n" \
                  "https://www.vimeo.com/11111111\n" \
                  "https://player.vimeo.com/video/11111111\n" \
                  "https://vimeo.com/channels/11111111\n" \
                  "https://vimeo.com/groups/name/videos/11111111\n" \
                  "https://vimeo.com/album/2222222/video/11111111\n" \
                  "https://vimeo.com/11111111?param=value\n" \
                  "https://novimeo.com/11111111\n" \
                  "bad https://novimeo.com/11111111\n" \
                  "https://novimeo.com/11111111 bad"
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertListEqual(comment_md.splitlines(), '<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                             '\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                             '\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                             '\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                             '\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                             '\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                             '\n<span class="video"><iframe src="https://player.vimeo.com/video/11111111" allowfullscreen></iframe></span>'
                             '\n<p><a href="https://novimeo.com/11111111">https://novimeo.com/11111111</a><br>'
                             'bad <a href="https://novimeo.com/11111111">https://novimeo.com/11111111</a><br>'
                             '<a href="https://novimeo.com/11111111">https://novimeo.com/11111111</a> bad</p>'.splitlines())

    def test_markdown_video(self):
        """
        markdown video
        """
        comment = "http://foo.bar/video.mp4\nhttp://foo.bar/<escaped>.mp4"
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertListEqual(comment_md.splitlines(), '<video controls><source src="http://foo.bar/video.mp4">'
                                                      '<a href="http://foo.bar/video.mp4">http://foo.bar/video.mp4</a></video>'
                                                      '\n<video controls><source src="http://foo.bar/&lt;escaped&gt;.mp4">'
                                                      '<a href="http://foo.bar/&lt;escaped&gt;.mp4">'
                                                      'http://foo.bar/&lt;escaped&gt;.mp4</a></video>'.splitlines())

    def test_markdown_audio(self):
        """
        markdown audio
        """
        comment = "http://foo.bar/audio.mp3\nhttp://foo.bar/<escaped>.mp3"
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertListEqual(comment_md.splitlines(), '<audio controls><source src="http://foo.bar/audio.mp3"><a href="http://foo.bar/audio.mp3">http://foo.bar/audio.mp3</a></audio>'
                             '\n<audio controls><source src="http://foo.bar/&lt;escaped&gt;.mp3"><a href="http://foo.bar/&lt;escaped&gt;.mp3">http://foo.bar/&lt;escaped&gt;.mp3</a></audio>'.splitlines())

    def test_markdown_poll(self):
        """
        markdown poll
        """
        comment = "[poll name=foo_1]\n" \
                  "1. opt 1\n" \
                  "2. opt 2\n" \
                  "3. opt 3\n" \
                  "[/poll]"
        md = Markdown(escape=True, hard_wrap=True)
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
            md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo_1]<br>1. opt 1<br>[/poll]</p>')
        self.assertEqual(md.get_polls(), {'polls': [], 'choices': []})

    def test_markdown_poll_invalid_no_options(self):
        """
        Should have at least two options
        """
        comment = "[poll name=foo_1]\n" \
                  "[/poll]"
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
            md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
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
        md = Markdown(escape=True, hard_wrap=True)
        comment_md = md.render(comment)
        self.assertEqual(comment_md, '<p>[poll name=foo mode=foo]<br>1. opt 1<br>2. opt 2<br>[/poll]</p>')
