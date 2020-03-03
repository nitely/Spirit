# -*- coding: utf-8 -*-

import warnings

from django.test import TestCase

from ..utils import deprecations


class UtilsDeprecations(TestCase):

    def setUp(self):
        pass

    def test_warn(self):
        with warnings.catch_warnings(record=True) as w:
            deprecations.warn("foo")
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(
                w[-1].category,
                deprecations.RemovedInNextVersionWarning))
            self.assertTrue('foo' in str(w[-1].message))
