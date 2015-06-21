# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='admin-category'),
    url(r'^list/$', views.index, name='admin-category-list'),
    url(r'^create/$', views.create, name='admin-category-create'),
    url(r'^update/(?P<category_id>\d+)/$', views.update, name='admin-category-update'),
]
