# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.comment_like",
                       url(r'^(?P<comment_id>\d+)/create/$', 'like_create', name='like-create'),
                       url(r'^(?P<pk>\d+)/delete/$', 'like_delete', name='like-delete'),
                       )
