# -*- coding: utf-8 -*-

from django.conf.urls import re_path

from . import views


app_name = 'bookmark'
urlpatterns = [
    re_path(r'^(?P<topic_id>[0-9]+)/create/$', views.create, name='create'),
    re_path(r'^(?P<topic_id>[0-9]+)/find/$', views.find, name='find'),
]
