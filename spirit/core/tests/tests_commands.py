# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.test import TestCase
from django.core.management import call_command
from django.utils.six import StringIO


class CommandsTests(TestCase):

    def test_command_spiritcompilemessages(self):
        """
        Should compile all locales under the spirit root folder
        """
        out = StringIO()
        err = StringIO()
        call_command('spiritcompilemessages', stdout=out, stderr=err)
        out_put = out.getvalue().strip().splitlines()
        out_put_err = err.getvalue().strip().splitlines()
        self.assertTrue(out_put[0].startswith("processing file django.po in"))
        self.assertEqual(out_put[-2], "ok")
        self.assertEqual(out_put_err, [])
