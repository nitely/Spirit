# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.admin.user",
                       url(r'^$', 'user_list', name='admin-user'),
                       url(r'^edit/(?P<user_id>\d+)/$', 'user_edit', name='admin-user-edit'),
                       url(r'^list/$', 'user_list', name='admin-user-list'),
                       url(r'^admins/$', 'user_admins', name='admin-user-admins'),
                       url(r'^mods/$', 'user_mods', name='admin-user-mods'),
                       url(r'^unactive/$', 'user_unactive', name='admin-user-unactive'),
                       )
