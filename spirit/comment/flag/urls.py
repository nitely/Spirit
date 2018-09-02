# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'flag'
urlpatterns = [
    url(r'^(?P<comment_id>[0-9]+)/create/$', views.create, name='create'),
]
