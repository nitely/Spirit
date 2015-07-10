# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<topic_id>\d+)/create/$', views.create, name='bookmark-create'),
    url(r'^(?P<topic_id>\d+)/find/$', views.find, name='bookmark-find'),
]
