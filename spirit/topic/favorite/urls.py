# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views


app_name = 'favorite'
urlpatterns = [
    url(r'^(?P<topic_id>[0-9]+)/create/$', views.create, name='create'),
    url(r'^(?P<pk>[0-9]+)/delete/$', views.delete, name='delete'),
]
