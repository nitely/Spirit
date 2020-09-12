#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys
import logging

import django
from django.test.runner import DiscoverRunner


os.environ['DJANGO_SETTINGS_MODULE'] = 'project.project.settings.test'


def setup_celery():
    try:
        from celery import Celery
    except ImportError:
        return
    app = Celery('test')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()


def log_warnings():
    logger = logging.getLogger('py.warnings')
    handler = logging.StreamHandler()
    logger.addHandler(handler)


def run_tests(reverse=False):
    sys.stdout.write(
        "\nRunning spirit test suite, using settings %(settings)r\n\n" %
        {"settings": os.environ['DJANGO_SETTINGS_MODULE']})
    return DiscoverRunner(reverse=reverse).run_tests([])


def start():
    django.setup()
    log_warnings()
    setup_celery()
    if run_tests() or run_tests(reverse=True):
        sys.exit(1)


if __name__ == "__main__":
    start()
