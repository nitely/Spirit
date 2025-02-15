from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Upgrade Spirit."

    def handle(self, *args, **options):
        call_command("migrate", stdout=self.stdout, stderr=self.stderr)
        call_command(
            "rebuild_index", stdout=self.stdout, stderr=self.stderr, interactive=False
        )
        call_command(
            "collectstatic", stdout=self.stdout, stderr=self.stderr, verbosity=0
        )
        self.stdout.write("ok")
