# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.list_unread, name='topic-notification-list-unread'),
    url(r'^list/$', views.index, name='topic-notification-list'),
    url(r'^(?P<topic_id>\d+)/create/$', views.create, name='topic-notification-create'),
    url(r'^(?P<pk>\d+)/update/$', views.update, name='topic-notification-update'),
    url(r'^ajax/$', views.list_ajax, name='topic-notification-ajax'),
]
