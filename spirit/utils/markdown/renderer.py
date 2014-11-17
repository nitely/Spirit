# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mistune


class Renderer(mistune.Renderer):

    def audio_link(self, link):
        return '<audio controls><source src="{link}"><a href="{link}">{link}</a></audio>\n'.format(link=link)

    def image_link(self, src, title, text):
        image = self.image(src, title, text)
        return '<p>{image}</p>\n'.format(image=image)

    def emoji(self, path):
        return '<img class="comment-emoji" src="{path}">'.format(path=path)

    def mention(self, username, url):
        return '<a class="comment-mention" href="{url}">@{username}</a>'.format(username=username, url=url)

    def video_link(self, link):
        return '<video controls><source src="{link}"><a href="{link}">{link}</a></video>\n'.format(link=link)

    def youtube(self, video_id):
        return '<span class="video"><iframe src="https://www.youtube.com/embed/{video_id}?feature=oembed" ' \
               'allowfullscreen></iframe></span>\n'.format(video_id=video_id)

    def vimeo(self, video_id):
        return '<span class="video"><iframe src="https://player.vimeo.com/video/{video_id}" ' \
               'allowfullscreen></iframe></span>\n'.format(video_id=video_id)
