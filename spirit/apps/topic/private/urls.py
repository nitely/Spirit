# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.private_list, name='private-list'),
    url(r'^created/$', views.private_created_list, name='private-created-list'),

    url(r'^publish/$', views.private_publish, name='private-publish'),
    url(r'^publish/(?P<user_id>\d+)/$', views.private_publish, name='private-publish'),

    url(r'^(?P<topic_id>\d+)/$', views.private_detail, kwargs={'slug': "", }, name='private-detail'),
    url(r'^(?P<topic_id>\d+)/(?P<slug>[\w-]+)/$', views.private_detail, name='private-detail'),

    url(r'^invite/(?P<topic_id>\d+)/$', views.private_access_create, name='private-access-create'),
    url(r'^remove/(?P<pk>\d+)/$', views.private_access_delete, name='private-access-remove'),
    url(r'^join/(?P<topic_id>\d+)/$', views.private_join, name='private-join'),
]
