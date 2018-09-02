# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'unread'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
