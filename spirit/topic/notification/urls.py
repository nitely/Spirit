# -*- coding: utf-8 -*-

from django.conf.urls import re_path

from . import views


app_name = 'notification'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^unread/$', views.index_unread, name='index-unread'),
    re_path(r'^ajax/$', views.index_ajax, name='index-ajax'),
    re_path(r'^(?P<topic_id>[0-9]+)/create/$', views.create, name='create'),
    re_path(r'^(?P<pk>[0-9]+)/update/$', views.update, name='update'),
    re_path(r'^mark/$', views.mark_all_as_read, name='mark-all-as-read'),
]
