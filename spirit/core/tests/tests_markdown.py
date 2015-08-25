# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.cache import cache
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import translation
from django.conf import settings

from ..tests import utils as test_utils
from ..utils.markdown import Markdown, quotify


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
