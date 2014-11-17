# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from spirit.views.category import CategoryList


urlpatterns = patterns("spirit.views.category",
                       url(r'^$', CategoryList.as_view(), name='category-list'),

                       url(r'^(?P<pk>\d+)/$', 'category_detail', kwargs={'slug': "", }, name='category-detail'),
                       url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', 'category_detail', name='category-detail'),
                       )
