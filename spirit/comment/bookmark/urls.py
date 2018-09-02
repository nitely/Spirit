# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'bookmark'
urlpatterns = [
    url(r'^(?P<topic_id>[0-9]+)/create/$', views.create, name='create'),
    url(r'^(?P<topic_id>[0-9]+)/find/$', views.find, name='find'),
]
