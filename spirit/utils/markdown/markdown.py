# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mistune

from .block import BlockLexer
from .inline import InlineLexer
from .renderer import Renderer


class Markdown(mistune.Markdown):

        def __init__(self, renderer=None, **kwargs):
            if renderer is None:
                renderer = Renderer()

            if kwargs.get('block', None) is None:
                kwargs['block'] = BlockLexer

            if kwargs.get('inline', None) is None:
                kwargs['inline'] = InlineLexer

            super(Markdown, self).__init__(renderer=renderer, **kwargs)

        def render(self, text):
            return super(Markdown, self).render(text).strip()

        def get_mentions(self):
            return self.inline.mentions

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
