# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.topic_favorite",
                       url(r'^(?P<topic_id>\d+)/create/$', 'favorite_create', name='favorite-create'),
                       url(r'^(?P<pk>\d+)/delete/$', 'favorite_delete', name='favorite-delete'),
                       )
