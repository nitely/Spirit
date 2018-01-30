# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from ...conf import settings
from ... import utils


class Command(BaseCommand):
    help = 'Creates or updates .po files and compiles them to .mo ' \
           'files for use with the builtin gettext support. Run ' \
           '`python manage.py spiritmakelocales > out` to read ' \
           'the output later (look for warnings)'

    requires_system_checks = False

    def handle(self, *args, **options):
        if not settings.ST_BASE_DIR.endswith('spirit'):
            raise CommandError(
                'settings.ST_BASE_DIR is not the spirit root folder, are you overriding it?'
            )

        for root, dirs, files in os.walk(settings.ST_BASE_DIR):
            if 'locale' not in dirs:
                continue

            with utils.pushd(root):
                call_command('makemessages', stdout=self.stdout, stderr=self.stderr)
                call_command('compilemessages', stdout=self.stdout, stderr=self.stderr)

        self.stdout.write('ok')
