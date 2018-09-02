# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'private'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^author/$', views.index_author, name='index-author'),

    url(r'^publish/$', views.publish, name='publish'),
    url(r'^publish/(?P<user_id>[0-9]+)/$', views.publish, name='publish'),

    url(r'^(?P<topic_id>[0-9]+)/$', views.detail, kwargs={'slug': "", }, name='detail'),
    url(r'^(?P<topic_id>[0-9]+)/(?P<slug>[\w-]+)/$', views.detail, name='detail'),

    url(r'^invite/(?P<topic_id>[0-9]+)/$', views.create_access, name='access-create'),
    url(r'^remove/(?P<pk>[0-9]+)/$', views.delete_access, name='access-remove'),
    url(r'^join/(?P<topic_id>[0-9]+)/$', views.join_in, name='join'),
]
