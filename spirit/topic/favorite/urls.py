# -*- coding: utf-8 -*-

from django.urls import re_path

from . import views


app_name = 'favorite'
urlpatterns = [
    re_path(r'^(?P<topic_id>[0-9]+)/create/$', views.create, name='create'),
    re_path(r'^(?P<pk>[0-9]+)/delete/$', views.delete, name='delete'),
]
