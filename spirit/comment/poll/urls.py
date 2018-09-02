# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'poll'
urlpatterns = [
    url(r'^close/(?P<pk>[0-9]+)/$', views.close_or_open, name='close'),
    url(r'^open/(?P<pk>[0-9]+)/$',
        views.close_or_open,
        kwargs={'close': False},
        name='open'),
    url(r'^vote/(?P<pk>[0-9]+)/$', views.vote, name='vote'),
    url(r'^voters/(?P<pk>[0-9]+)/$', views.voters, name='voters'),
]
