# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),

    url(r'^(?P<pk>\d+)/$', views.detail, kwargs={'slug': "", 'course_no': None}, name='detail'),
    url(r'^(?P<pk>\d+)/(?P<course_no>\d+)/$', views.detail, kwargs={'slug': "", }, name='detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.detail, kwargs={'course_no': None}, name='detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/(?P<course_no>\d+)/$', views.detail, name='detail'),
]
