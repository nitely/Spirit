# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import Signal


comment_moved = Signal(providing_args=['comments', 'topic_from'])

