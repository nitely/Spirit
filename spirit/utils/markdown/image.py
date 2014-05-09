#-*- coding: utf-8 -*-

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class ImagifyExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add('imagify',
                             ImagifyPreprocessor(md),
                             '_end')


class ImagifyPreprocessor(Preprocessor):

    def run(self, lines):
        new_lines = []

        def imagify(match):
            return u'![image](%s)' % match.group(0)

        for line in lines:
            if line.strip():
                line = re.sub(ur'^https?://[^\s]+/(?P<image_name>[^\s]+)\.'
                              ur'(?P<extension>png|jpg|jpeg|gif|bmp|tif|tiff)'
                              ur'(\?[^\s]+)?$', imagify, line, flags=re.UNICODE)

            new_lines.append(line)

        return new_lines


def makeExtension(configs=None):
    return ImagifyExtension(configs=configs)