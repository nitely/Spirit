# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mistune

from .block import BlockLexer
from .inline import InlineLexer
from .renderer import Renderer


class Markdown(mistune.Markdown):

    def __init__(self, no_follow=True):
        renderer = Renderer(
            escape=True,
            hard_wrap=True,
            no_follow=no_follow
        )
        super(Markdown, self).__init__(
            renderer=renderer,
            block=BlockLexer,
            inline=InlineLexer,
            parse_block_html=False,
            parse_inline_html=False
        )

    # Override
    def __call__(self, text):
        return super(Markdown, self).__call__(text).strip()

    def render(self, text):
        return self(text)

    def get_mentions(self):
        return self.inline.mentions

    def get_polls(self):
        return self.block.polls

    def output_block_link(self):
        return self.renderer.block_link(
            link=self.token['link'])

    def output_audio_link(self):
        return self.renderer.audio_link(
            link=self.token['link'])

    def output_image_link(self):
        return self.renderer.image_link(
            src=self.token['src'],
            title=self.token['title'],
            text=self.token['text']
        )

    def output_video_link(self):
        return self.renderer.video_link(
            link=self.token['link']
        )

    def output_youtube_link(self):
        return self.renderer.youtube_link(
            video_id=self.token['video_id'],
            start_hours=self.token['start_hours'],
            start_minutes=self.token['start_minutes'],
            start_seconds=self.token['start_seconds']
        )

    def output_vimeo_link(self):
        return self.renderer.vimeo_link(
            video_id=self.token['video_id']
        )

    def output_gfycat_link(self):
        return self.renderer.gfycat_link(
            video_id=self.token['video_id']
        )

    def output_poll(self):
        try:
            name = self.token['name']
        except KeyError:
            return self.renderer.poll_raw(
                poll_txt=self.token['raw']
            )
        else:
            return self.renderer.poll(name=name)
