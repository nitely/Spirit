#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import logging

import django
from django.test.runner import DiscoverRunner


EXAMPLE = 'example' in sys.argv

if EXAMPLE:
    # Run tests with example settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'example.project.settings.test'  # pragma: no cover
else:
    # Run tests with tests settings
    os.environ['DJANGO_SETTINGS_MODULE'] = 'spirit.settings_tests'


def log_warnings():
    logger = logging.getLogger('py.warnings')
    handler = logging.StreamHandler()
    logger.addHandler(handler)


def run_tests():
    sys.stdout.write("\nRunning spirit test suite, using settings %(settings)r\n\n"
                     % {"settings": os.environ['DJANGO_SETTINGS_MODULE'], })
    test_runner = DiscoverRunner()
    # todo: remove in spirit 0.4
    failures = test_runner.run_tests([
        "spirit.admin",
        "spirit.category",
        "spirit.comment",
        "spirit.comment.bookmark",
        "spirit.comment.flag",
        "spirit.comment.history",
        "spirit.comment.like",
        "spirit.core",
        "spirit.search",
        "spirit.topic",
        "spirit.topic.favorite",
        "spirit.topic.moderate",
        "spirit.topic.notification",
        "spirit.topic.poll",
        "spirit.topic.private",
        "spirit.topic.unread",
        "spirit.user",
    ])
    sys.exit(failures)


def start():
    django.setup()
    log_warnings()
    run_tests()


if __name__ == "__main__":
    start()
