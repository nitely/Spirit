# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.deleted, name='admin-topic'),
    url(r'^deleted/$', views.deleted, name='admin-topic-deleted'),
    url(r'^closed/$', views.closed, name='admin-topic-closed'),
    url(r'^pinned/$', views.pinned, name='admin-topic-pinned'),
]
