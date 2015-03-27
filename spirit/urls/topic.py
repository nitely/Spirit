# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.topic",
                       url(r'^publish/$', 'topic_publish', name='topic-publish'),
                       url(r'^publish/(?P<category_id>\d+)/$', 'topic_publish', name='topic-publish'),

                       url(r'^update/(?P<pk>\d+)/$', 'topic_update', name='topic-update'),

                       url(r'^(?P<pk>\d+)/$', 'topic_detail', kwargs={'slug': "", }, name='topic-detail'),
                       url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', 'topic_detail', name='topic-detail'),

                       url(r'^active/$', 'topic_active_list', name='topic-active'),
                       )
