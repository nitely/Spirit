# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from subprocess import call
import os

from django.core.management.base import BaseCommand, CommandError

from ...conf import settings
from ... import utils


class Command(BaseCommand):
    help = 'Pushes all locale sources listed in ./.tx/config to transifex'

    requires_system_checks = False

    def handle(self, *args, **options):
        # Requires `pip install transifex-client``
        # also: ``$ tx init`` to create credentials
        root = os.path.split(settings.ST_BASE_DIR)[0]
        tx_dir = os.path.join(root, '.tx')

        if not os.path.isdir(tx_dir):
            raise CommandError('Can\'t find the .tx folder in %s' % (root, ))

        with utils.pushd(root):
            # -t will update the translation,
            # only if it was updated locally,
            # so use when fixing something
            call(["tx", "push", "-s", "--skip"])

        self.stdout.write('ok')
