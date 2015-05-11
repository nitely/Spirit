# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^publish/$', views.topic_publish, name='topic-publish'),
    url(r'^publish/(?P<category_id>\d+)/$', views.topic_publish, name='topic-publish'),

    url(r'^update/(?P<pk>\d+)/$', views.topic_update, name='topic-update'),

    url(r'^(?P<pk>\d+)/$', views.topic_detail, kwargs={'slug': "", }, name='topic-detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.topic_detail, name='topic-detail'),

    url(r'^active/$', views.topic_active_list, name='topic-active'),
]
