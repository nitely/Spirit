# -*- coding: utf-8 -*-

import mistune

from django.utils.html import escape
from django.template.defaultfilters import truncatechars

from spirit.core.conf import settings


def sanitize_url(url):
    url = escape(url)  # & -> &amp; ...
    parts = url.split(':', 1)

    # If there's not protocol then
    # make sure is a relative path
    if len(parts) == 1 and url.startswith('/'):
        return url

    if parts[0] in settings.ST_ALLOWED_URL_PROTOCOLS:
        return url

    return ''


class Renderer(mistune.Renderer):

    def block_math(self, text):
        return '<p class="math">$$%s$$</p>\n' % escape(text)

    def block_math_brackets(self, text):
        return '<p class="math">\\[%s\\]</p>\n' % escape(text)

    def block_latex(self, text, name):
        name = escape(name)
        text = escape(text)
        return '<p class="math">\\begin{%s}%s\\end{%s}</p>\n' % (name, text, name)

    def math(self, text):
        return '<span class="math">\\(%s\\)</span>' % escape(text)

    # Override
    def autolink(self, link, is_email=False):
        link = sanitize_url(link)
        text = truncatechars(link, settings.ST_COMMENT_MAX_URL_LEN)
        if is_email:
            link = 'mailto:%s' % link
        no_follow = ''
        if self.options['no_follow']:
            no_follow = ' rel="nofollow"'
        result = '<a{no_follow} href="{href}">{text}</a>'
        return result.format(
            no_follow=no_follow, href=link, text=text)

    # Override
    def link(self, link, title, text):
        link = sanitize_url(link)
        no_follow = ''
        if self.options['no_follow']:
            no_follow = ' rel="nofollow"'
        title = title or ''
        if title:
            title = ' title="%s"' % escape(title)
        result = '<a{no_follow} href="{href}"{title}>{text}</a>'
        return result.format(
            no_follow=no_follow, href=link, title=title, text=text)

    # Override
    def _image(self, src, title, text):
        src = sanitize_url(src)
        text = escape(text)

        if title:
            title = escape(title)
            html = '<img src="%s" alt="%s" title="%s"' % (src, text, title)
        else:
            html = '<img src="%s" alt="%s"' % (src, text)

        if self.options.get('use_xhtml'):
            return '%s />' % html

        return '%s>' % html

    def image(self, src, title, text):
        image = self._image(src, title, text)
        return '<span class="img">{image}</span>'.format(image=image)

    def emoji(self, name_class, name_raw):
        return (
            '<i class="tw tw-{name_class}" '
            'title=":{name_raw}:"></i>'
            .format(
                name_class=name_class,
                name_raw=name_raw))

    def mention(self, username, url):
        return (
            '<a class="comment-mention" rel="nofollow" '
            'href="{url}">@{username}</a>'
            .format(
                username=username,
                url=url))

    def block_link(self, link):
        return '<p>%s</p>\n' % self.autolink(link)

    def audio_link(self, link):
        link = sanitize_url(link)
        return (
            '<audio controls><source src="{link}">'
            '<a rel="nofollow" href="{link}">'
            '{link}</a></audio>\n'
            .format(link=link))

    def image_link(self, src, title, text):
        image = self._image(src, title, text)
        return '<p><span class="img_block">{image}</span></p>\n'.format(image=image)

    def video_link(self, link):
        link = sanitize_url(link)
        return (
            '<video controls><source src="{link}">'
            '<a rel="nofollow" href="{link}">{link}</a></video>\n'
            .format(link=link))

    def youtube_link(
            self,
            video_id,
            start_hours=None,
            start_minutes=None,
            start_seconds=None):
        timestamp = 0

        if start_hours:
            timestamp += int(start_hours.replace('h', '')) * 60 * 60

        if start_minutes:
            timestamp += int(start_minutes.replace('m', '')) * 60

        if start_seconds:
            timestamp += int(start_seconds.replace('s', ''))

        if timestamp:
            timestamp = '&start=%s' % timestamp
        else:
            timestamp = ''

        return (
            '<span class="video"><iframe '
            'src="https://www.youtube.com/embed/{video_id}?html5=1{timestamp}" '
            'allowfullscreen></iframe></span>\n'
            .format(
                video_id=video_id,
                timestamp=timestamp))

    def vimeo_link(self, video_id):
        return (
            '<span class="video"><iframe '
            'src="https://player.vimeo.com/video/{video_id}" '
            'allowfullscreen></iframe></span>\n'
            .format(video_id=video_id))

    def gfycat_link(self, video_id):
        return (
            '<span class="video"><iframe src="https://gfycat.com/ifr/{video_id}" '
            'frameborder="0" scrolling="no" allowfullscreen></iframe></span>\n'
            .format(video_id=video_id))

    def poll(self, name):
        return '<poll name={name}>\n'.format(name=name)

    def poll_raw(self, poll_txt):
        poll_txt = poll_txt.replace('\n', '<br>')
        return '<p>{poll}</p>\n'.format(poll=poll_txt)
