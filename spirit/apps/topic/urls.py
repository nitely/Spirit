# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^publish/$', views.publish, name='topic-publish'),
    url(r'^publish/(?P<category_id>\d+)/$', views.publish, name='topic-publish'),

    url(r'^update/(?P<pk>\d+)/$', views.update, name='topic-update'),

    url(r'^(?P<pk>\d+)/$', views.detail, kwargs={'slug': "", }, name='topic-detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.detail, name='topic-detail'),

    url(r'^active/$', views.index_active, name='topic-active'),
]
