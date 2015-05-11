# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.notification_list_unread, name='topic-notification-list-unread'),
    url(r'^list/$', views.notification_list, name='topic-notification-list'),
    url(r'^(?P<topic_id>\d+)/create/$', views.notification_create, name='topic-notification-create'),
    url(r'^(?P<pk>\d+)/update/$', views.notification_update, name='topic-notification-update'),
    url(r'^ajax/$', views.notification_ajax, name='topic-notification-ajax'),
]
