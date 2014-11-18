# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.topic_unread",
                       url(r'^$', 'topic_unread_list', name='topic-unread-list'),
                       )
