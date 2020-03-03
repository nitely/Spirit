# -*- coding: utf-8 -*-

import os
import io

from django.test import TestCase
from django.core.management import call_command

from ..management.commands import spiritcompilemessages
from ..management.commands import spirittxpush
from ..management.commands import spiritinstall
from ..management.commands import spiritupgrade


class CommandsTests(TestCase):

    def test_command_spiritcompilemessages(self):
        """
        Should compile all locales under the spirit root folder
        """
        commands = []
        dirs = []

        def call_mock(command, **kwargs):
            commands.append(command)
            dirs.append(os.getcwd())

        org_call, spiritcompilemessages.call_command = spiritcompilemessages.call_command, call_mock
        try:
            out = io.StringIO()
            err = io.StringIO()
            call_command('spiritcompilemessages', stdout=out, stderr=err)
            out_put = out.getvalue().strip().splitlines()
            out_put_err = err.getvalue().strip().splitlines()
            self.assertEqual(commands[0], 'compilemessages')
            self.assertEqual(len(dirs), 22)
            self.assertEqual(out_put[-1], "ok")
            self.assertEqual(out_put_err, [])
        finally:
            spiritcompilemessages.call_command = org_call

    def test_command_spirittxpush(self):
        """
        Should run the tx command
        """
        def call_mock(command):
            self._command = command

        org_call, spirittxpush.call = spirittxpush.call, call_mock
        try:
            out = io.StringIO()
            err = io.StringIO()
            call_command('spirittxpush', stdout=out, stderr=err)
            out_put = out.getvalue().strip().splitlines()
            out_put_err = err.getvalue().strip().splitlines()
            self.assertEqual(
                self._command,
                ['tx', 'push', '--source', '--skip', '--language', 'en'])
            self.assertEqual(out_put[-1], "ok")
            self.assertEqual(out_put_err, [])
        finally:
            spirittxpush.call = org_call

    def test_command_spiritinstall(self):
        """
        Should run migrations, create cache table and collect statics
        """
        command_list = []

        def call_mock(command, **kwargs):
            command_list.append(command)

        org_call, spiritinstall.call_command = spiritinstall.call_command, call_mock
        try:
            out = io.StringIO()
            err = io.StringIO()
            call_command('spiritinstall', stdout=out, stderr=err)
            out_put = out.getvalue().strip().splitlines()
            out_put_err = err.getvalue().strip().splitlines()
            self.assertEqual(out_put[-1], "ok")
            self.assertEqual(out_put_err, [])
            self.assertEqual(command_list, ["migrate", "createcachetable", "collectstatic"])
        finally:
            spiritinstall.call = org_call

    def test_command_spiritupgrade(self):
        """
        Should run migrations, rebuild search index and collect statics
        """
        command_list = []

        def call_mock(command, **kwargs):
            command_list.append(command)

        org_call, spiritupgrade.call_command = spiritupgrade.call_command, call_mock
        try:
            out = io.StringIO()
            err = io.StringIO()
            call_command('spiritupgrade', stdout=out, stderr=err)
            out_put = out.getvalue().strip().splitlines()
            out_put_err = err.getvalue().strip().splitlines()
            self.assertEqual(out_put[-1], "ok")
            self.assertEqual(out_put_err, [])
            self.assertEqual(command_list, ["migrate", "rebuild_index", "collectstatic"])
        finally:
            spiritupgrade.call = org_call
