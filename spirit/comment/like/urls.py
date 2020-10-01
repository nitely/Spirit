# -*- coding: utf-8 -*-

from django.conf.urls import re_path

from . import views


app_name = 'like'
urlpatterns = [
    re_path(r'^(?P<comment_id>[0-9]+)/create/$', views.create, name='create'),
    re_path(r'^(?P<pk>[0-9]+)/delete/$', views.delete, name='delete'),
]
