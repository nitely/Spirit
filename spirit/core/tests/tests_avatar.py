# -*- coding: utf-8 -*-

from django.test import TestCase
from django.template import Template, Context

from . import utils


class AvatarTemplateTagTests(TestCase):
    def setUp(self):
        self.user = utils.create_user()

    def test_get_avatar_color(self):
        out = Template(
            "{% load spirit_tags %}"
            "{% get_avatar_color 0 %}"
        ).render(Context(autoescape=False))
        self.assertEqual(out, "hsl(0, 75%, 25%)")
        out = Template(
            "{% load spirit_tags %}"
            "{% get_avatar_color 36 %}"
        ).render(Context(autoescape=False))
        self.assertEqual(out, "hsl(360, 75%, 25%)")
        out = Template(
            "{% load spirit_tags %}"
            "{% get_avatar_color 37 %}"
        ).render(Context(autoescape=False))
        self.assertEqual(out, "hsl(0, 75%, 25%)")
