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
        "spirit.apps.admin",
        "spirit.apps.category",
        "spirit.apps.comment",
        "spirit.apps.comment.bookmark",
        "spirit.apps.comment.flag",
        "spirit.apps.comment.history",
        "spirit.apps.comment.like",
        "spirit.apps.core",
        "spirit.apps.search",
        "spirit.apps.topic",
        "spirit.apps.topic.favorite",
        "spirit.apps.topic.moderate",
        "spirit.apps.topic.notification",
        "spirit.apps.topic.poll",
        "spirit.apps.topic.private",
        "spirit.apps.topic.unread",
        "spirit.apps.user",
    ])
    sys.exit(failures)


def start():
    django.setup()
    log_warnings()
    run_tests()


if __name__ == "__main__":
    start()
