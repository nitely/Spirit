# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.user_list, name='admin-user'),
    url(r'^edit/(?P<user_id>\d+)/$', views.user_edit, name='admin-user-edit'),
    url(r'^list/$', views.user_list, name='admin-user-list'),
    url(r'^admins/$', views.user_admins, name='admin-user-admins'),
    url(r'^mods/$', views.user_mods, name='admin-user-mods'),
    url(r'^unactive/$', views.user_unactive, name='admin-user-unactive'),
]
