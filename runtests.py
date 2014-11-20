#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import logging

os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings_test_runner'

import django
from django.test.runner import DiscoverRunner


def log_warnings():
    logger = logging.getLogger('py.warnings')
    handler = logging.StreamHandler()
    logger.addHandler(handler)


def run_tests():
    test_runner = DiscoverRunner()
    failures = test_runner.run_tests(["tests", ])
    sys.exit(failures)


def start():
    django.setup()
    log_warnings()
    run_tests()


if __name__ == "__main__":
    start()
