#!/usr/bin/env python

import logging
import os
import sys

if __name__ == "__main__":
    logging.captureWarnings(True)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ project_name }}.settings.dev")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
