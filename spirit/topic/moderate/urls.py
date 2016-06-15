# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^delete/(?P<pk>\d+)/$', views.delete, name='delete'),
    url(r'^undelete/(?P<pk>\d+)/$', views.undelete, name='undelete'),

    url(r'^lock/(?P<pk>\d+)/$', views.lock, name='lock'),
    url(r'^unlock/(?P<pk>\d+)/$', views.unlock, name='unlock'),

    url(r'^pin/(?P<pk>\d+)/$', views.pin, name='pin'),
    url(r'^unpin/(?P<pk>\d+)/$', views.unpin, name='unpin'),

    url(r'^global-pin/(?P<pk>\d+)/$', views.global_pin, name='global-pin'),
    url(r'^global-unpin/(?P<pk>\d+)/$', views.global_unpin, name='global-unpin'),
]
