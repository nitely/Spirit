# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from subprocess import call
import os

from django.core.management.base import BaseCommand, CommandError

from ...conf import settings
from ... import utils


class Command(BaseCommand):
    help = 'Pulls all the local files listed in ./.tx/config from transifex'

    requires_system_checks = False

    def handle(self, *args, **options):
        # todo: test!
        # Requires ``pip install transifex-client``
        # ``tx pull -l es-ES`` to pull a new lang
        root = os.path.split(settings.ST_BASE_DIR)[0]
        tx_dir = os.path.join(root, '.tx')

        if not os.path.isdir(tx_dir):
            raise CommandError('Can\'t find the .tx folder in %s' % (root, ))

        with utils.pushd(root):
            call(["tx", "pull", "-f"])

        self.stdout.write('ok')
