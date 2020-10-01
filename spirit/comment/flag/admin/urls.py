# -*- coding: utf-8 -*-

from django.conf.urls import re_path

from . import views


app_name = 'flag'
urlpatterns = [
    re_path(r'^$', views.opened, name='index'),
    re_path(r'^opened/$', views.opened, name='opened'),
    re_path(r'^closed/$', views.closed, name='closed'),
    re_path(r'^(?P<pk>[0-9]+)/$', views.detail, name='detail'),
]
