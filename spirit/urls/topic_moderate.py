# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from spirit.views.topic_moderate import TopicModerateDelete, TopicModerateUnDelete, \
    TopicModerateLock, TopicModerateUnLock, TopicModeratePin, TopicModerateUnPin, \
    TopicModerateGlobalPin, TopicModerateGlobalUnPin


urlpatterns = patterns(
    "spirit.views.topic_moderate",

    url(r'^delete/(?P<pk>\d+)/$', TopicModerateDelete.as_view(), name='topic-delete'),
    url(r'^undelete/(?P<pk>\d+)/$', TopicModerateUnDelete.as_view(), name='topic-undelete'),

    url(r'^lock/(?P<pk>\d+)/$', TopicModerateLock.as_view(), name='topic-lock'),
    url(r'^unlock/(?P<pk>\d+)/$', TopicModerateUnLock.as_view(), name='topic-unlock'),

    url(r'^pin/(?P<pk>\d+)/$', TopicModeratePin.as_view(), name='topic-pin'),
    url(r'^unpin/(?P<pk>\d+)/$', TopicModerateUnPin.as_view(), name='topic-unpin'),

    url(r'^globallypin/(?P<pk>\d+)/$', TopicModerateGlobalPin.as_view(), name='topic-global-pin'),
    url(r'^ungloballypin/(?P<pk>\d+)/$', TopicModerateGlobalUnPin.as_view(), name='topic-global-unpin'),
    )
