# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^author/$', views.index_author, name='index-author'),

    url(r'^publish/$', views.publish, name='publish'),
    url(r'^publish/(?P<user_id>\d+)/$', views.publish, name='publish'),

    url(r'^(?P<topic_id>\d+)/$', views.detail, kwargs={'slug': "", }, name='detail'),
    url(r'^(?P<topic_id>\d+)/(?P<slug>[\w-]+)/$', views.detail, name='detail'),

    url(r'^invite/(?P<topic_id>\d+)/$', views.create_access, name='access-create'),
    url(r'^remove/(?P<pk>\d+)/$', views.delete_access, name='access-remove'),
    url(r'^join/(?P<topic_id>\d+)/$', views.join_in, name='join'),
]
