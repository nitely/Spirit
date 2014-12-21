# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from spirit.views.topic_moderate import TopicModerateDelete, TopicModerateLock, \
    TopicModeratePin, TopicModerateGlobalPin


urlpatterns = patterns(
    "spirit.views.topic_moderate",

    url(r'^delete/(?P<pk>\d+)/$', TopicModerateDelete.as_view(), kwargs={'value': True, }, name='topic-delete'),
    url(r'^undelete/(?P<pk>\d+)/$', TopicModerateDelete.as_view(), kwargs={'value': False, }, name='topic-undelete'),

    url(r'^lock/(?P<pk>\d+)/$', TopicModerateLock.as_view(), kwargs={'value': True, }, name='topic-lock'),
    url(r'^unlock/(?P<pk>\d+)/$', TopicModerateLock.as_view(), kwargs={'value': False, }, name='topic-unlock'),

    url(r'^pin/(?P<pk>\d+)/$', TopicModeratePin.as_view(), kwargs={'value': True, }, name='topic-pin'),
    url(r'^unpin/(?P<pk>\d+)/$', TopicModeratePin.as_view(), kwargs={'value': False, }, name='topic-unpin'),

    url(r'^globallypin/(?P<pk>\d+)/$', TopicModerateGlobalPin.as_view(), kwargs={'value': True, },
        name='topic-global-pin'),
    url(r'^ungloballypin/(?P<pk>\d+)/$', TopicModerateGlobalPin.as_view(), kwargs={'value': False, },
        name='topic-global-unpin'),
    )
