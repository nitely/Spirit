# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='private-list'),
    url(r'^created/$', views.index_author, name='private-created-list'),

    url(r'^publish/$', views.publish, name='private-publish'),
    url(r'^publish/(?P<user_id>\d+)/$', views.publish, name='private-publish'),

    url(r'^(?P<topic_id>\d+)/$', views.detail, kwargs={'slug': "", }, name='private-detail'),
    url(r'^(?P<topic_id>\d+)/(?P<slug>[\w-]+)/$', views.detail, name='private-detail'),

    url(r'^invite/(?P<topic_id>\d+)/$', views.create_access, name='private-access-create'),
    url(r'^remove/(?P<pk>\d+)/$', views.delete_access, name='private-access-remove'),
    url(r'^join/(?P<topic_id>\d+)/$', views.join_in, name='private-join'),
]
