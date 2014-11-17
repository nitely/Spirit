# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.dispatch import Signal


topic_poll_pre_vote = Signal(providing_args=['poll, user'])
topic_poll_post_vote = Signal(providing_args=['poll, user'])
