# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

from ... import utils


class Command(BaseCommand):
    help = 'Compiles .po files created by makemessages to .mo ' \
           'files for use with the builtin gettext support'

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
                call_command('compilemessages', stdout=self.stdout, stderr=self.stderr)

        self.stdout.write('ok')
        self.stdout.write('Run \'python manage.py spirittxpush\' to push the changes to transifex.')
