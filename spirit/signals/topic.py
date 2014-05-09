#-*- coding: utf-8 -*-

from django.dispatch import Signal


topic_viewed = Signal(providing_args=['request', 'topic'])
topic_post_moderate = Signal(providing_args=['user', 'topic', 'action'])