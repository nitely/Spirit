# -*- coding: utf-8 -*-

from django.test import TestCase, override_settings
from django.template.loader import render_to_string

from . import utils


class TemplatesTests(TestCase):
    def setUp(self):
        self.user = utils.create_user()

    @override_settings(ST_MATH_JAX=True)
    def test_math_jax(self):
        tpl = render_to_string('spirit/_footer.html')
        self.assertTrue('MathJax.js' in tpl)
        self.assertTrue('x-mathjax-config' in tpl)

    @override_settings(ST_MATH_JAX=False)
    def test_math_jax_disabled(self):
        tpl = render_to_string('spirit/_footer.html')
        self.assertFalse('MathJax.js' in tpl)
        self.assertFalse('x-mathjax-config' in tpl)
