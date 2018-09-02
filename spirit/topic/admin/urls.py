# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'topic'
urlpatterns = [
    url(r'^$', views.deleted, name='index'),
    url(r'^deleted/$', views.deleted, name='deleted'),
    url(r'^closed/$', views.closed, name='closed'),
    url(r'^pinned/$', views.pinned, name='pinned'),
]
