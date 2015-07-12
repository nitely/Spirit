# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^delete/(?P<pk>\d+)/$', views.DeleteView.as_view(), name='delete'),
    url(r'^undelete/(?P<pk>\d+)/$', views.UnDeleteView.as_view(), name='undelete'),

    url(r'^lock/(?P<pk>\d+)/$', views.LockView.as_view(), name='lock'),
    url(r'^unlock/(?P<pk>\d+)/$', views.UnLockView.as_view(), name='unlock'),

    url(r'^pin/(?P<pk>\d+)/$', views.PinView.as_view(), name='pin'),
    url(r'^unpin/(?P<pk>\d+)/$', views.UnPinView.as_view(), name='unpin'),

    url(r'^global-pin/(?P<pk>\d+)/$', views.GlobalPinView.as_view(), name='global-pin'),
    url(r'^global-unpin/(?P<pk>\d+)/$', views.GlobalUnPinView.as_view(), name='global-unpin'),
]
