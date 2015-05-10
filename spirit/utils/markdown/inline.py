# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import re
import copy
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.storage import staticfiles_storage
import mistune

from spirit.utils.markdown.utils.emoji import emojis


User = get_user_model()


class InlineGrammar(mistune.InlineGrammar):

    emoji = re.compile(
        r'^:(?P<emoji>[A-Za-z0-9_\-\+]+?):'
    )

    mention = re.compile(
        r'^@(?P<username>[\w.@+-]+)',
        flags=re.UNICODE
    )

    # Override
    def hard_wrap(self):
        # Adds ":" and "@" as a valid text character, so we can match emojis and mentions.
        self.linebreak = re.compile(r'^ *\n(?!\s*$)')
        self.text = re.compile(
            r'^[\s\S]+?(?=[\\<!\[_*`:@~]|https?://| *\n|$)'
        )


class InlineLexer(mistune.InlineLexer):

    default_features = copy.copy(mistune.InlineLexer.default_features)
    default_features.insert(0, 'emoji')
    default_features.insert(0, 'mention')

    def __init__(self, renderer, rules=None, **kwargs):
        if rules is None:
            rules = InlineGrammar()

        super(InlineLexer, self).__init__(renderer, rules, **kwargs)

        self.mentions = {}
        self._mention_count = 0

    def output_emoji(self, m):
        emoji = m.group('emoji')

        if emoji not in emojis:
            return m.group(0)

        image = emoji + '.png'
        rel_path = os.path.join('spirit', 'emojis', image).replace('\\', '/')
        path = staticfiles_storage.url(rel_path)

        return self.renderer.emoji(path)

    def output_mention(self, m):
        username = m.group('username')

        # Already mentioned?
        if username in self.mentions:
            user = self.mentions[username]
            return self.renderer.mention(username, user.st.get_absolute_url())

        # Mentions limiter
        if self._mention_count >= settings.ST_MENTIONS_PER_COMMENT:
            return m.group(0)

        # We increase this before doing the query to avoid abuses
        self._mention_count += 1

        # New mention
        try:
            user = User.objects\
                .select_related('st')\
                .get(username=username)
        except User.DoesNotExist:
            return m.group(0)

        self.mentions[username] = user
        return self.renderer.mention(username, user.st.get_absolute_url())
