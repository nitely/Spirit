import os
from subprocess import call

from django.core.management.base import BaseCommand, CommandError

from ... import utils
from ...conf import settings


class Command(BaseCommand):
    help = "Pushes english locale source"

    requires_system_checks = []

    def handle(self, *args, **options):
        # Requires `pip install transifex-client``
        # also: ``$ tx init`` to create credentials
        root = os.path.split(settings.ST_BASE_DIR)[0]
        tx_dir = os.path.join(root, ".tx")

        if not os.path.isdir(tx_dir):
            raise CommandError(f"Can't find the .tx folder in {root}")

        with utils.pushd(root):
            # -t will update the translation,
            # only if it was updated locally,
            # so use when fixing something
            call(["tx", "push", "--source", "--skip", "--language", "en"])

        self.stdout.write("ok")
