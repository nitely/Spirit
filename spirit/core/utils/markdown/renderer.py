# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mistune


class Renderer(mistune.Renderer):

    # Override
    def autolink(self, link, is_email=False):
        text = link

        if is_email:
            link = 'mailto:%s' % link

        if self.options['no_follow']:
            return '<a rel="nofollow" href="%s">%s</a>' % (link, text)

        return '<a href="%s">%s</a>' % (link, text)

    # Override
    def link(self, link, title, text):
        if link.startswith('javascript:'):
            link = ''

        if not title:
            if self.options['no_follow']:
                return '<a rel="nofollow" href="%s">%s</a>' % (link, text)

            return '<a href="%s">%s</a>' % (link, text)

        title = mistune.escape(title, quote=True)

        if self.options['no_follow']:
            return '<a rel="nofollow" href="%s" title="%s">%s</a>' % (link, title, text)

        return '<a href="%s" title="%s">%s</a>' % (link, title, text)

    def audio_link(self, link):
        return '<audio controls><source src="{link}">' \
               '<a rel="nofollow" href="{link}">{link}</a></audio>\n'.format(link=link)

    def image_link(self, src, title, text):
        image = self.image(src, title, text)
        return '<p>{image}</p>\n'.format(image=image)

    def emoji(self, name_class, name_raw):
        # todo: add no-follow to links since we are going to need migration to fix emojis
        return '<i class="tw tw-{name_class}" title=":{name_raw}:"></i>'.format(
            name_class=name_class,
            name_raw=name_raw
        )

    def mention(self, username, url):
        return '<a class="comment-mention" rel="nofollow" href="{url}">@{username}</a>'.format(
            username=username,
            url=url
        )

    def video_link(self, link):
        return '<video controls><source src="{link}">' \
               '<a rel="nofollow" href="{link}">{link}</a></video>\n'.format(link=link)

    def youtube(self, video_id):
        return '<span class="video"><iframe src="https://www.youtube.com/embed/{video_id}?html5=1" ' \
               'allowfullscreen></iframe></span>\n'.format(video_id=video_id)

    def vimeo(self, video_id):
        return '<span class="video"><iframe src="https://player.vimeo.com/video/{video_id}" ' \
               'allowfullscreen></iframe></span>\n'.format(video_id=video_id)

    def poll(self, name):
        return '<poll name={name}>\n'.format(name=name)

    def poll_raw(self, poll_txt):
        poll_txt = poll_txt.replace('\n', '<br>')
        return '<p>{poll}</p>\n'.format(poll=poll_txt)
