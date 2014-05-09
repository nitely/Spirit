#-*- coding: utf-8 -*-

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


# Try to get the video ID. Works for URLs of the form:
# * https://www.youtube.com/watch?v=Z0UISCEe52Y
# * http://youtu.be/afyK1HSFfgw
# * https://www.youtube.com/embed/vsF0K3Ou1v0
PATTERN_RE = ur'^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)(?P<id>[a-zA-Z0-9_\-]{11})$'


class YouTubefyExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add('youtubefy',
                             YouTubefyPreprocessor(md),
                             '_end')


class YouTubefyPreprocessor(Preprocessor):

    def run(self, lines):
        new_lines = []

        def youtubefy(match):
            video_id = match.group("id")
            html = u'<span class="video"><iframe src="https://www.youtube.com/embed/{video_id}?feature=oembed" ' \
                   u'allowfullscreen></iframe></span>'.format(video_id=video_id)
            return self.markdown.htmlStash.store(html, safe=True)

        for line in lines:
            if line.strip():
                line = re.sub(PATTERN_RE, youtubefy, line, flags=re.UNICODE)

            new_lines.append(line)

        return new_lines


def makeExtension(configs=None):
    return YouTubefyExtension(configs=configs)