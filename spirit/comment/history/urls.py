# -*- coding: utf-8 -*-

from django.conf.urls import re_path

from . import views


app_name = 'history'
urlpatterns = [
    re_path(r'^(?P<comment_id>[0-9]+)/$', views.detail, name='detail'),
]
