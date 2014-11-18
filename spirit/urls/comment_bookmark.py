# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.comment_bookmark",
                       url(r'^(?P<topic_id>\d+)/create/$', 'bookmark_create', name='bookmark-create'),
                       url(r'^(?P<topic_id>\d+)/find/$', 'bookmark_find', name='bookmark-find'),
                       )
