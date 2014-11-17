# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import Signal


comment_posted = Signal(providing_args=['comment', 'mentions'])
comment_pre_update = Signal(providing_args=['comment', ])
comment_post_update = Signal(providing_args=['comment', ])
comment_moved = Signal(providing_args=['comments', 'topic_from'])
