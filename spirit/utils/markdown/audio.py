#-*- coding: utf-8 -*-

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from django.utils.html import escape as html_escape


PATTERN_RE = ur'^https?://[^\s]+\.(mp3|ogg|wav)(\?[^\s]+)?$'


class AudiofyExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add('audiofy',
                             AudiofyPreprocessor(md),
                             '_end')


class AudiofyPreprocessor(Preprocessor):

    def run(self, lines):
        new_lines = []

        def audiofy(match):
            url = match.group(0)
            url = html_escape(url)
            html = u'<audio controls><source src="{url}"><a href="{url}">{url}</a></audio>'.format(url=url)
            return self.markdown.htmlStash.store(html, safe=True)

        for line in lines:
            if line.strip():
                line = re.sub(PATTERN_RE, audiofy, line, flags=re.UNICODE)

            new_lines.append(line)

        return new_lines


def makeExtension(configs=None):
    return AudiofyExtension(configs=configs)