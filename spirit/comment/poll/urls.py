# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^close/(?P<pk>\d+)/$', views.close, name='close'),
    url(r'^vote/(?P<pk>\d+)/$', views.vote, name='vote'),
]
