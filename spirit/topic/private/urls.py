# -*- coding: utf-8 -*-

from django.conf.urls import re_path

from . import views


app_name = 'private'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^author/$', views.index_author, name='index-author'),

    re_path(r'^publish/$', views.publish, name='publish'),
    re_path(r'^publish/(?P<user_id>[0-9]+)/$', views.publish, name='publish'),

    re_path(r'^(?P<topic_id>[0-9]+)/$', views.detail, kwargs={'slug': "", }, name='detail'),
    re_path(r'^(?P<topic_id>[0-9]+)/(?P<slug>[\w-]+)/$', views.detail, name='detail'),

    re_path(r'^invite/(?P<topic_id>[0-9]+)/$', views.create_access, name='access-create'),
    re_path(r'^remove/(?P<pk>[0-9]+)/$', views.delete_access, name='access-remove'),
    re_path(r'^join/(?P<topic_id>[0-9]+)/$', views.join_in, name='join'),
]
