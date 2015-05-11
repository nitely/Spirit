# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^delete/(?P<pk>\d+)/$', views.TopicModerateDelete.as_view(), name='topic-delete'),
    url(r'^undelete/(?P<pk>\d+)/$', views.TopicModerateUnDelete.as_view(), name='topic-undelete'),

    url(r'^lock/(?P<pk>\d+)/$', views.TopicModerateLock.as_view(), name='topic-lock'),
    url(r'^unlock/(?P<pk>\d+)/$', views.TopicModerateUnLock.as_view(), name='topic-unlock'),

    url(r'^pin/(?P<pk>\d+)/$', views.TopicModeratePin.as_view(), name='topic-pin'),
    url(r'^unpin/(?P<pk>\d+)/$', views.TopicModerateUnPin.as_view(), name='topic-unpin'),

    url(r'^globallypin/(?P<pk>\d+)/$', views.TopicModerateGlobalPin.as_view(), name='topic-global-pin'),
    url(r'^ungloballypin/(?P<pk>\d+)/$', views.TopicModerateGlobalUnPin.as_view(), name='topic-global-unpin'),
]
