# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils.six.moves import input  # noqa


class Command(BaseCommand):
    help = 'Pulls, make locales and pushes (in that order) the .po files to transifex'

    requires_system_checks = False

    def handle(self, *args, **options):
        # todo: test!
        # Requires ``pip install transifex-client``

        call_command('spiritmakelocales', stdout=self.stdout, stderr=self.stderr)
        call_command('spirittxpush', stdout=self.stdout, stderr=self.stderr)
        call_command('spirittxpull', stdout=self.stdout, stderr=self.stderr)
        call_command('spiritmakelocales', stdout=self.stdout, stderr=self.stderr)

        self.stdout.write('ok')
