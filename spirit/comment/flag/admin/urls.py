# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.opened, name='admin-flag'),
    url(r'^open/$', views.opened, name='admin-flag-open'),
    url(r'^closed/$', views.closed, name='admin-flag-closed'),
    url(r'^(?P<pk>\d+)/$', views.detail, name='admin-flag-detail'),
]
