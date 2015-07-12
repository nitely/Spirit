# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.opened, name='index'),
    url(r'^opened/$', views.opened, name='opened'),
    url(r'^closed/$', views.closed, name='closed'),
    url(r'^(?P<pk>\d+)/$', views.detail, name='detail'),
]
