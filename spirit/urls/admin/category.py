# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.admin.category",
                       url(r'^$', 'category_list', name='admin-category'),
                       url(r'^list/$', 'category_list', name='admin-category-list'),
                       url(r'^create/$', 'category_create', name='admin-category-create'),
                       url(r'^update/(?P<category_id>\d+)/$', 'category_update', name='admin-category-update'),
                       )
