# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mistune

from .block import BlockLexer
from .inline import InlineLexer
from .renderer import Renderer


class Markdown(mistune.Markdown):

    def __init__(self, no_follow=True):
        renderer = Renderer(no_follow=no_follow)
        super(Markdown, self).__init__(
            renderer=renderer,
            block=BlockLexer,
            inline=InlineLexer,
            escape=True,
            hard_wrap=True
        )

    def render(self, text):
        return super(Markdown, self).render(text).strip()

    def get_mentions(self):
        return self.inline.mentions

    def get_polls(self):
        return self.block.polls

    def parse_audio_link(self):
        return self.renderer.audio_link(link=self.token['link'])

    def parse_image_link(self):
        return self.renderer.image_link(src=self.token['src'], title=self.token['title'], text=self.token['text'])

    def parse_video_link(self):
        return self.renderer.video_link(link=self.token['link'])

    def parse_youtube(self):
        return self.renderer.youtube(video_id=self.token['video_id'])

    def parse_vimeo(self):
        return self.renderer.vimeo(video_id=self.token['video_id'])

    def parse_poll(self):
        try:
            name = self.token['name']
        except KeyError:
            return self.renderer.poll_raw(poll_txt=self.token['raw'])
        else:
            return self.renderer.poll(name=name)
