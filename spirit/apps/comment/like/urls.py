# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<comment_id>\d+)/create/$', views.like_create, name='like-create'),
    url(r'^(?P<pk>\d+)/delete/$', views.like_delete, name='like-delete'),
]
