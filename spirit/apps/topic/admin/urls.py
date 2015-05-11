# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.topic_deleted, name='admin-topic'),
    url(r'^deleted/$', views.topic_deleted, name='admin-topic-deleted'),
    url(r'^closed/$', views.topic_closed, name='admin-topic-closed'),
    url(r'^pinned/$', views.topic_pinned, name='admin-topic-pinned'),
]
