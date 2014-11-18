# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.admin.topic",
                       url(r'^$', 'topic_deleted', name='admin-topic'),
                       url(r'^deleted/$', 'topic_deleted', name='admin-topic-deleted'),
                       url(r'^closed/$', 'topic_closed', name='admin-topic-closed'),
                       url(r'^pinned/$', 'topic_pinned', name='admin-topic-pinned'),
                       )
