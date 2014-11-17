# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.topic_private",
                       url(r'^$', 'private_list', name='private-list'),
                       url(r'^created/$', 'private_created_list', name='private-created-list'),

                       url(r'^publish/$', 'private_publish', name='private-publish'),
                       url(r'^publish/(?P<user_id>\d+)/$', 'private_publish', name='private-publish'),

                       url(r'^(?P<topic_id>\d+)/$', 'private_detail', kwargs={'slug': "", }, name='private-detail'),
                       url(r'^(?P<topic_id>\d+)/(?P<slug>[\w-]+)/$', 'private_detail', name='private-detail'),

                       url(r'^invite/(?P<topic_id>\d+)/$', 'private_access_create', name='private-access-create'),
                       url(r'^remove/(?P<pk>\d+)/$', 'private_access_delete', name='private-access-remove'),
                       url(r'^join/(?P<topic_id>\d+)/$', 'private_join', name='private-join'),
                       )
