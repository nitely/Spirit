# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.topic_notification",
                       url(r'^$', 'notification_list_unread', name='topic-notification-list-unread'),
                       url(r'^list/$', 'notification_list', name='topic-notification-list'),
                       url(r'^(?P<topic_id>\d+)/create/$', 'notification_create', name='topic-notification-create'),
                       url(r'^(?P<pk>\d+)/update/$', 'notification_update', name='topic-notification-update'),
                       url(r'^ajax/$', 'notification_ajax', name='topic-notification-ajax'),
                       )
