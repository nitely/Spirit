# -*- coding: utf-8 -*-

from django.urls import re_path

from . import views


app_name = 'unread'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
]
