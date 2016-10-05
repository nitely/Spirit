# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.template import Template, Context

from . import utils


class GravatarTemplateTagTests(TestCase):
    def setUp(self):
        self.user = utils.create_user()

    def test_gravatar_url(self):
        """
        gravatar url
        """
        out = Template(
            "{% load spirit_tags %}"
            "{% get_gravatar_url user 21 %}"
        ).render(Context({'user': self.user, }, autoescape=False))
        self.assertEqual(out, "https://www.gravatar.com/avatar/472860d1aad501ba9795fb31e94ad42f?d=identicon&s=21&r=g")
