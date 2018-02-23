# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import copy

import mistune

from .parsers.poll import PollParser


class BlockGrammar(mistune.BlockGrammar):

    block_link = re.compile(
        r'^https?://[^\s]+'
        r'(?:\n+|$)'
    )

    # These used to be their own matching rule,
    # but matching once instead of X times is way faster
    sub_block_link = re.compile(
        r'(?:'
            # Try to get the video ID. Works for URLs of the form:
            # * https://www.youtube.com/watch?v=Z0UISCEe52Y
            # * http://youtu.be/afyK1HSFfgw
            # * https://www.youtube.com/embed/vsF0K3Ou1v0
            #
            # Also works for timestamps:
            # * https://www.youtube.com/watch?v=Z0UISCEe52Y&t=1m30s
            # * https://www.youtube.com/watch?v=O1QQajfobPw&t=1h1m38s
            # * https://www.youtube.com/watch?v=O1QQajfobPw&feature=youtu.be&t=3698
            # * https://youtu.be/O1QQajfobPw?t=3698
            # * https://youtu.be/O1QQajfobPw?t=1h1m38s
            r'(?P<youtube_link>'
                r'^https?://(?:www\.)?'
                r'(?:youtube\.com/watch\?v='
                r'|youtu\.be/'
                r'|youtube\.com/embed/)'
                r'(?P<youtube_id>[a-zA-Z0-9_\-]{11})'
                r'(?:(?:&|\?)(?:'
                    r'|(?:t=(?P<youtube_start_hours>[0-9]{1,2}h)?'
                    r'(?P<youtube_start_minutes>[0-9]{1,4}m)?'
                    r'(?P<youtube_start_seconds>[0-9]{1,5}s?)?)'
                    r'|(?:[^&\s]+)'
                r')){,10}'
                r'(?:\n+|$)'
            r')|'
            # Try to get the video ID. Works for URLs of the form:
            # * https://vimeo.com/11111111
            # * https://www.vimeo.com/11111111
            # * https://player.vimeo.com/video/11111111
            # * https://vimeo.com/channels/11111111
            # * https://vimeo.com/groups/name/videos/11111111
            # * https://vimeo.com/album/2222222/video/11111111
            # * https://vimeo.com/11111111?param=value
            r'(?P<vimeo_link>'
                r'^https?://(?:www\.|player\.)?'
                r'vimeo\.com/'
                r'(?:channels/'
                r'|groups/[^/]+/videos/'
                r'|album/(?:[0-9]+)/video/'
                r'|video/)?'
                r'(?P<vimeo_id>[0-9]+)'
                r'(?:\?[^\s]+)?'
                r'(?:\n+|$)'
            r')|'
            # Try to get the video ID. Works for URLs of the form:
            # * https://gfycat.com/videoid
            # * https://www.gfycat.com/videoid
            # * http://gfycat.com/videoid
            # * http://www.gfycat.com/videoid
            r'(?P<gfycat_link>'
                r'^https?://(?:www\.)?'
                r'gfycat\.com/'
                r'(?P<gfycat_id>\w+)'
                r'(?:\?[^\s]+)?'
                r'(?:\n+|$)'
            r')|'
            r'(?P<audio_link>'
                r'^https?://[^\s]+\.(?:mp3|ogg|wav)'
                r'(?:\?[^\s]+)?'
                r'(?:\n+|$)'
            r')|'
            r'(?P<image_link>'
                r'^https?://[^\s]+/(?P<image_name>[^\s]+)\.'
                r'(?:png|jpg|jpeg|gif|bmp|tif|tiff)'
                r'(?:\?[^\s]+)?'
                r'(?:\n+|$)'
            r')|'
            r'(?P<video_link>'
                r'^https?://[^\s]+\.(?:mov|mp4|webm|ogv)'
                r'(?:\?[^\s]+)?'
                r'(?:\n+|$)'
            r')'
        r')'
    )

    # Capture polls:
    # [poll name=foo min=1 max=1 close=1d mode=default]
    # # Which opt you prefer?
    # 1. opt 1
    # 2. opt 2
    # [/poll]
    poll = re.compile(
        r'^(?:\[poll'
        r'((?:\s+name=(?P<name>[\w\-_]+))'
        r'(?:\s+min=(?P<min>[0-9]+))?'
        r'(?:\s+max=(?P<max>[0-9]+))?'
        r'(?:\s+close=(?P<close>[0-9]+)d)?'
        r'(?:\s+mode=(?P<mode>(default|secret)))?'
        r'|(?P<invalid_params>[^\]]*))'
        r'\])\n'
        r'((?:#\s*(?P<title>[^\n]+\n))?'
        r'(?P<choices>(?:[0-9]+\.\s*[^\n]+\n){2,})'
        r'|(?P<invalid_body>(?:[^\n]+\n)*))'
        r'(?:\[/poll\])'
    )


class BlockLexer(mistune.BlockLexer):

    default_rules = copy.copy(mistune.BlockLexer.default_rules)
    default_rules.insert(0, 'block_link')
    default_rules.insert(0, 'poll')

    _sub_block_links = (
        'audio_link',
        'image_link',
        'video_link',
        'youtube_link',
        'vimeo_link',
        'gfycat_link'
    )

    def __init__(self, rules=None, **kwargs):
        if rules is None:
            rules = BlockGrammar()

        super(BlockLexer, self).__init__(rules=rules, **kwargs)

        self.polls = {
            'polls': [],
            'choices': []
        }

    def parse_block_link(self, m):
        link = m.group(0).strip()
        sub_match = BlockGrammar.sub_block_link.match(link)

        if sub_match is not None:
            groups = sub_match.groupdict()
        else:
            groups = {}

        for sbl in self._sub_block_links:
            if groups.get(sbl, None) is not None:
                getattr(self, 'parse_%s' % sbl)(sub_match)
                break
        else:  # no-break
            self.tokens.append({
                'type': 'block_link',
                'link': link
            })

    def parse_audio_link(self, m):
        self.tokens.append({
            'type': 'audio_link',
            'link': m.group(0).strip()
        })

    def parse_image_link(self, m):
        link = m.group(0).strip()
        title = m.group('image_name').strip()
        self.tokens.append({
            'type': 'image_link',
            'src': link,
            'title': title,
            'text': title
        })

    def parse_video_link(self, m):
        self.tokens.append({
            'type': 'video_link',
            'link': m.group(0).strip()
        })

    def parse_youtube_link(self, m):
        self.tokens.append({
            'type': 'youtube_link',
            'video_id': m.group("youtube_id"),
            'start_hours': m.group("youtube_start_hours"),
            'start_minutes': m.group("youtube_start_minutes"),
            'start_seconds': m.group("youtube_start_seconds"),
        })

    def parse_vimeo_link(self, m):
        self.tokens.append({
            'type': 'vimeo_link',
            'video_id': m.group("vimeo_id")
        })

    def parse_gfycat_link(self, m):
        self.tokens.append({
            'type': 'gfycat_link',
            'video_id': m.group("gfycat_id")
        })

    def parse_poll(self, m):
        parser = PollParser(polls=self.polls, data=m.groupdict())

        if parser.is_valid():
            poll = parser.cleaned_data['poll']
            choices = parser.cleaned_data['choices']
            self.polls['polls'].append(poll)
            self.polls['choices'].extend(choices)
            self.tokens.append({
                'type': 'poll',
                'name': poll['name']
            })
        else:
            self.tokens.append({
                'type': 'poll',
                'raw': m.group(0)
            })
