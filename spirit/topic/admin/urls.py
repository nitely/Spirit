# -*- coding: utf-8 -*-

from django.conf.urls import re_path

from . import views


app_name = 'topic'
urlpatterns = [
    re_path(r'^$', views.deleted, name='index'),
    re_path(r'^deleted/$', views.deleted, name='deleted'),
    re_path(r'^closed/$', views.closed, name='closed'),
    re_path(r'^pinned/$', views.pinned, name='pinned'),
]
