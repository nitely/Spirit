#-*- coding: utf-8 -*-

import re

from markdown import Extension
from markdown.preprocessors import Preprocessor

from django.utils.html import escape as html_escape


PATTERN_RE = ur'^https?://[^\s]+\.(mov|mp4|webm|ogv)(\?[^\s]+)?$'


class VideofyExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add('videofy',
                             VideofyPreprocessor(md),
                             '_end')


class VideofyPreprocessor(Preprocessor):

    def run(self, lines):
        new_lines = []

        def videofy(match):
            url = match.group(0)
            url = html_escape(url)
            html = u'<video controls><source src="{url}"><a href="{url}">{url}</a></video>'.format(url=url)
            return self.markdown.htmlStash.store(html, safe=True)

        for line in lines:
            if line.strip():
                line = re.sub(PATTERN_RE, videofy, line, flags=re.UNICODE)

            new_lines.append(line)

        return new_lines


def makeExtension(configs=None):
    return VideofyExtension(configs=configs)