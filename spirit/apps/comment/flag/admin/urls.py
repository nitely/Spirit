# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.flag_open, name='admin-flag'),
    url(r'^open/$', views.flag_open, name='admin-flag-open'),
    url(r'^closed/$', views.flag_closed, name='admin-flag-closed'),
    url(r'^(?P<pk>\d+)/$', views.flag_detail, name='admin-flag-detail'),
]
