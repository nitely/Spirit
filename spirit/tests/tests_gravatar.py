#-*- coding: utf-8 -*-

from django.test import TestCase
from django.template import Template, Context, TemplateSyntaxError

import utils


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
        ).render(Context({'user': self.user, }))
        self.assertEqual(out, "http://www.gravatar.com/avatar/441cf33d0e5b36a95bae87e400783ca4?s=21&r=g&d=identicon")