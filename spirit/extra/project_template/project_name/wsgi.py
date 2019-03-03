# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import logging
import os

from django.core.wsgi import get_wsgi_application


logging.captureWarnings(True)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ project_name }}.settings.dev")

application = get_wsgi_application()
