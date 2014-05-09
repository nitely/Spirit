#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.topic",
    url(r'^publish/$', 'topic_publish', name='topic-publish'),
    url(r'^publish/(?P<category_id>\d+)/$', 'topic_publish', name='topic-publish'),

    url(r'^update/(?P<pk>\d+)/$', 'topic_update', name='topic-update'),

    url(r'^(?P<pk>\d+)/$', 'topic_detail', kwargs={'slug': "", }, name='topic-detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', 'topic_detail', name='topic-detail'),

    url(r'^active/$', 'topics_active', name='topic-active'),

    url(r'^delete/(?P<pk>\d+)/$', 'topic_moderate', kwargs={'remove': True, 'value': True}, name='topic-delete'),
    url(r'^undelete/(?P<pk>\d+)/$', 'topic_moderate', kwargs={'remove': True, 'value': False}, name='topic-undelete'),

    url(r'^lock/(?P<pk>\d+)/$', 'topic_moderate', kwargs={'lock': True, 'value': True}, name='topic-lock'),
    url(r'^unlock/(?P<pk>\d+)/$', 'topic_moderate', kwargs={'lock': True, 'value': False}, name='topic-unlock'),

    url(r'^pin/(?P<pk>\d+)/$', 'topic_moderate', kwargs={'pin': True, 'value': True}, name='topic-pin'),
    url(r'^unpin/(?P<pk>\d+)/$', 'topic_moderate', kwargs={'pin': True, 'value': False}, name='topic-unpin'),
)