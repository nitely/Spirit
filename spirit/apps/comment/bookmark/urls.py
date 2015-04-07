# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns(
    "spirit.apps.comment.bookmark.views",
    url(r'^(?P<topic_id>\d+)/create/$', 'bookmark_create', name='bookmark-create'),
    url(r'^(?P<topic_id>\d+)/find/$', 'bookmark_find', name='bookmark-find'),
    )
