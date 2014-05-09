#-*- coding: utf-8 -*-

import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()


class MentionifyExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add('mentionify',
                             MentionifyPreprocessor(md),
                             '_end')


class MentionifyPreprocessor(Preprocessor):

    def run(self, lines):
        new_lines = []
        matches = set()
        mentions = {}

        def mentionify(match):
            username = match.group(2)

            if len(matches) >= settings.ST_MENTIONS_PER_COMMENT:
                return match.group(0)

            if username in matches:
                return match.group(0)

            matches.add(username)

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return match.group(0)

            mentions[username] = user

            return u'%s[@%s](%s)' % (match.group(1), username, user.get_absolute_url())

        for line in lines:
            if line.strip() and not line.startswith('>'):  # exclude code/quote
                line = re.sub(ur'([^\w]?)@(?P<username>[\w.@+-]+)', mentionify, line, flags=re.UNICODE)

            new_lines.append(line)

        # markdown_instance
        self.markdown.mentions = mentions

        return new_lines


def makeExtension(configs=None):
    return MentionifyExtension(configs=configs)