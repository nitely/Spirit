# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import Signal


comment_like_post_create = Signal(providing_args=['comment', ])
comment_like_post_delete = Signal(providing_args=['comment', ])
