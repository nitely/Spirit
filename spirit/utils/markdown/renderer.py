#-*- coding: utf-8 -*-

import mistune


class Renderer(mistune.Renderer):

    def audio_link(self, link):
        return u'<audio controls><source src="{link}"><a href="{link}">{link}</a></audio>\n'.format(link=link)

    def image_link(self, src, title, text):
        image = self.image(src, title, text)
        return u'<p>{image}</p>\n'.format(image=image)

    def emoji(self, path):
        return u'<img class="comment-emoji" src="{path}">'.format(path=path)

    def mention(self, username, url):
        return u'<a class="comment-mention" href="{url}">@{username}</a>'.format(username=username, url=url)

    def video_link(self, link):
        return u'<video controls><source src="{link}"><a href="{link}">{link}</a></video>\n'.format(link=link)

    def youtube(self, video_id):
        return u'<span class="video"><iframe src="https://www.youtube.com/embed/{video_id}?feature=oembed" ' \
               u'allowfullscreen></iframe></span>\n'.format(video_id=video_id)

    def vimeo(self, video_id):
        return u'<span class="video"><iframe src="https://player.vimeo.com/video/{video_id}" ' \
               u'allowfullscreen></iframe></span>\n'.format(video_id=video_id)