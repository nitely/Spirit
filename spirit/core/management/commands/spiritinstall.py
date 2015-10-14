# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Install Spirit.'

    def handle(self, *args, **options):
        # todo: add arg --no-input
        call_command('migrate', stdout=self.stdout, stderr=self.stderr)
        call_command('createcachetable', stdout=self.stdout, stderr=self.stderr)
        call_command('collectstatic', stdout=self.stdout, stderr=self.stderr, verbosity=0)
        self.stdout.write('ok')
