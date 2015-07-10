# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='admin-user'),
    url(r'^edit/(?P<user_id>\d+)/$', views.edit, name='admin-user-edit'),
    url(r'^list/$', views.index, name='admin-user-list'),
    url(r'^admins/$', views.admins, name='admin-user-admins'),
    url(r'^mods/$', views.mods, name='admin-user-mods'),
    url(r'^unactive/$', views.unactive, name='admin-user-unactive'),
]
