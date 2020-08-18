# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views


app_name = 'moderate'
urlpatterns = [
    url(r'^delete/(?P<pk>[0-9]+)/$', views.delete, name='delete'),
    url(r'^undelete/(?P<pk>[0-9]+)/$', views.undelete, name='undelete'),

    url(r'^lock/(?P<pk>[0-9]+)/$', views.lock, name='lock'),
    url(r'^unlock/(?P<pk>[0-9]+)/$', views.unlock, name='unlock'),

    url(r'^pin/(?P<pk>[0-9]+)/$', views.pin, name='pin'),
    url(r'^unpin/(?P<pk>[0-9]+)/$', views.unpin, name='unpin'),

    url(r'^global-pin/(?P<pk>[0-9]+)/$', views.global_pin, name='global-pin'),
    url(r'^global-unpin/(?P<pk>[0-9]+)/$', views.global_unpin, name='global-unpin'),
    url(r'^for-logged/(?P<pk>[0-9]+)/$', views.for_logged, name='for-logged'),
    url(r'^for-non-logged/(?P<pk>[0-9]+)/$', views.for_non_logged, name='for-non-logged'),
]
