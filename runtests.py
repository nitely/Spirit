#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import logging

import django
from django.test.runner import DiscoverRunner


os.environ['DJANGO_SETTINGS_MODULE'] = 'project.project.settings.test'


def log_warnings():
    logger = logging.getLogger('py.warnings')
    handler = logging.StreamHandler()
    logger.addHandler(handler)


def run_tests():
    sys.stdout.write(
        "\nRunning spirit test suite, using settings %(settings)r\n\n" %
        {"settings": os.environ['DJANGO_SETTINGS_MODULE']})
    test_runner = DiscoverRunner()
    failures = test_runner.run_tests([])
    sys.exit(failures)


def start():
    django.setup()
    log_warnings()
    run_tests()


if __name__ == "__main__":
    start()
