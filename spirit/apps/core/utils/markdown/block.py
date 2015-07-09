# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import copy

import mistune


class BlockGrammar(mistune.BlockGrammar):

    audio_link = re.compile(
        r'^https?://[^\s]+\.(mp3|ogg|wav)'
        r'(\?[^\s]+)?'
        r'(?:\n+|$)'
    )

    image_link = re.compile(
        r'^https?://[^\s]+/(?P<image_name>[^\s]+)\.'
        r'(?P<extension>png|jpg|jpeg|gif|bmp|tif|tiff)'
        r'(\?[^\s]+)?'
        r'(?:\n+|$)'
    )

    video_link = re.compile(
        r'^https?://[^\s]+\.(mov|mp4|webm|ogv)'
        r'(\?[^\s]+)?'
        r'(?:\n+|$)'
    )

    # Try to get the video ID. Works for URLs of the form:
    # * https://www.youtube.com/watch?v=Z0UISCEe52Y
    # * http://youtu.be/afyK1HSFfgw
    # * https://www.youtube.com/embed/vsF0K3Ou1v0
    youtube = re.compile(
        r'^https?://(www\.)?'
        r'(youtube\.com/watch\?v='
        r'|youtu\.be/'
        r'|youtube\.com/embed/)'
        r'(?P<id>[a-zA-Z0-9_\-]{11})'
        r'(?:\n+|$)'
    )

    # Try to get the video ID. Works for URLs of the form:
    # * https://vimeo.com/11111111
    # * https://www.vimeo.com/11111111
    # * https://player.vimeo.com/video/11111111
    # * https://vimeo.com/channels/11111111
    # * https://vimeo.com/groups/name/videos/11111111
    # * https://vimeo.com/album/2222222/video/11111111
    # * https://vimeo.com/11111111?param=value
    vimeo = re.compile(
        r'^https?://(www\.|player\.)?'
        r'vimeo\.com/'
        r'(channels/'
        r'|groups/[^/]+/videos/'
        r'|album/(\d+)/video/'
        r'|video/)?'
        r'(?P<id>\d+)'
        r'(\?[^\s]+)?'
        r'(?:\n+|$)'
    )


class BlockLexer(mistune.BlockLexer):

    default_features = copy.copy(mistune.BlockLexer.default_features)
    default_features.insert(0, 'audio_link')
    default_features.insert(0, 'image_link')
    default_features.insert(0, 'video_link')
    default_features.insert(0, 'youtube')
    default_features.insert(0, 'vimeo')

    def __init__(self, rules=None, **kwargs):
        if rules is None:
            rules = BlockGrammar()

        super(BlockLexer, self).__init__(rules=rules, **kwargs)

    def parse_audio_link(self, m):
        link = mistune.escape(m.group(0).strip(), quote=True)
        self.tokens.append({'type': 'audio_link', 'link': link})

    def parse_image_link(self, m):
        link = mistune.escape(m.group(0).strip(), quote=True)
        title = mistune.escape(m.group('image_name').strip(), quote=True)
        self.tokens.append({'type': 'image_link', 'src': link, 'title': title, 'text': title})

    def parse_video_link(self, m):
        link = mistune.escape(m.group(0).strip(), quote=True)
        self.tokens.append({'type': 'video_link', 'link': link})

    def parse_youtube(self, m):
        self.tokens.append({'type': 'youtube', 'video_id': m.group("id")})

    def parse_vimeo(self, m):
        self.tokens.append({'type': 'vimeo', 'video_id': m.group("id")})
