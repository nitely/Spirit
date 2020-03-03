# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views


app_name = 'history'
urlpatterns = [
    url(r'^(?P<comment_id>[0-9]+)/$', views.detail, name='detail'),
]
