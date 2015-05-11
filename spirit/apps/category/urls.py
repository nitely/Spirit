# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.CategoryList.as_view(), name='category-list'),

    url(r'^(?P<pk>\d+)/$', views.category_detail, kwargs={'slug': "", }, name='category-detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.category_detail, name='category-detail'),
]