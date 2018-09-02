# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'category'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^(?P<pk>[0-9]+)/$', views.detail, kwargs={'slug': "", }, name='detail'),
    url(r'^(?P<pk>[0-9]+)/(?P<slug>[\w-]+)/$', views.detail, name='detail'),
]
