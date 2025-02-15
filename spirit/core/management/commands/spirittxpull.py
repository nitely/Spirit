import os
from subprocess import call

from django.core.management.base import BaseCommand, CommandError

from ... import utils
from ...conf import settings


class Command(BaseCommand):
    help = "Pulls all the local files listed in ./.tx/config from transifex"

    requires_system_checks = []

    def handle(self, *args, **options):
        # todo: test!
        # Requires ``pip install transifex-client``
        # ``tx pull -l es-ES`` to pull a new lang
        root = os.path.split(settings.ST_BASE_DIR)[0]
        tx_dir = os.path.join(root, ".tx")

        if not os.path.isdir(tx_dir):
            raise CommandError(f"Can't find the .tx folder in {root}")

        with utils.pushd(root):
            call(["tx", "pull", "--force"])

        self.stdout.write("ok")
