# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url

from . import views


urlpatterns = [
    url(r'^$', views.category_list, name='admin-category'),
    url(r'^list/$', views.category_list, name='admin-category-list'),
    url(r'^create/$', views.category_create, name='admin-category-create'),
    url(r'^update/(?P<category_id>\d+)/$', views.category_update, name='admin-category-update'),
]
