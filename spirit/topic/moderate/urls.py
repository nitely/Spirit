# -*- coding: utf-8 -*-

from django.urls import re_path

from . import views


app_name = 'moderate'
urlpatterns = [
    re_path(r'^delete/(?P<pk>[0-9]+)/$', views.delete, name='delete'),
    re_path(r'^undelete/(?P<pk>[0-9]+)/$', views.undelete, name='undelete'),

    re_path(r'^lock/(?P<pk>[0-9]+)/$', views.lock, name='lock'),
    re_path(r'^unlock/(?P<pk>[0-9]+)/$', views.unlock, name='unlock'),

    re_path(r'^pin/(?P<pk>[0-9]+)/$', views.pin, name='pin'),
    re_path(r'^unpin/(?P<pk>[0-9]+)/$', views.unpin, name='unpin'),

    re_path(r'^global-pin/(?P<pk>[0-9]+)/$', views.global_pin, name='global-pin'),
    re_path(r'^global-unpin/(?P<pk>[0-9]+)/$', views.global_unpin, name='global-unpin'),
]
