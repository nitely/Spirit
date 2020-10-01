# -*- coding: utf-8 -*-

from django.conf.urls import re_path

from . import views


app_name = 'poll'
urlpatterns = [
    re_path(r'^close/(?P<pk>[0-9]+)/$', views.close_or_open, name='close'),
    re_path(r'^open/(?P<pk>[0-9]+)/$',
        views.close_or_open,
        kwargs={'close': False},
        name='open'),
    re_path(r'^vote/(?P<pk>[0-9]+)/$', views.vote, name='vote'),
    re_path(r'^voters/(?P<pk>[0-9]+)/$', views.voters, name='voters'),
]
