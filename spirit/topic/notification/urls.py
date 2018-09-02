# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'notification'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^unread/$', views.index_unread, name='index-unread'),
    url(r'^ajax/$', views.index_ajax, name='index-ajax'),
    url(r'^(?P<topic_id>[0-9]+)/create/$', views.create, name='create'),
    url(r'^(?P<pk>[0-9]+)/update/$', views.update, name='update'),
]
