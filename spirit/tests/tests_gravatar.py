# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.template import Template, Context, TemplateSyntaxError
from django.utils import six

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
        ).render(Context({'user': self.user, }))
        # Argument order may change between py2 and py3
        six.assertRegex(self, out, 'http://www.gravatar.com/avatar/441cf33d0e5b36a95bae87e400783ca4\?[srd]=\w+&[srd]=\w+&[srd]=\w+')
