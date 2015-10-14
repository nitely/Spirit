# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^close/(?P<pk>\d+)/$', views.close_or_open, name='close'),
    url(r'^open/(?P<pk>\d+)/$', views.close_or_open, kwargs={'close': False}, name='open'),
    url(r'^vote/(?P<pk>\d+)/$', views.vote, name='vote'),
    url(r'^voters/(?P<pk>\d+)/$', views.voters, name='voters'),
]
