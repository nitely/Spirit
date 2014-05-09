#-*- coding: utf-8 -*-

import re

from markdown import Extension
from markdown.preprocessors import Preprocessor


# Try to get the video ID. Works for URLs of the form:
# * https://vimeo.com/11111111
# * https://www.vimeo.com/11111111
# * https://player.vimeo.com/video/11111111
# * https://vimeo.com/channels/11111111
# * https://vimeo.com/groups/name/videos/11111111
# * https://vimeo.com/album/2222222/video/11111111
# * https://vimeo.com/11111111?param=value
PATTERN_RE = ur'^https?://(www\.|player\.)?vimeo\.com/(channels/|groups/[^/]+/videos/|album/(\d+)/video/|video/)?' \
             ur'(?P<id>\d+)(\?[^\s]+)?$'


class VimeofyExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add('vimeofy',
                             VimeofyPreprocessor(md),
                             '_end')


class VimeofyPreprocessor(Preprocessor):

    def run(self, lines):
        new_lines = []

        def vimeofy(match):
            video_id = match.group("id")
            html = u'<span class="video"><iframe src="https://player.vimeo.com/video/{video_id}" ' \
                   u'allowfullscreen></iframe></span>'.format(video_id=video_id)
            return self.markdown.htmlStash.store(html, safe=True)

        for line in lines:
            if line.strip():
                line = re.sub(PATTERN_RE, vimeofy, line, flags=re.UNICODE)

            new_lines.append(line)

        return new_lines


def makeExtension(configs=None):
    return VimeofyExtension(configs=configs)