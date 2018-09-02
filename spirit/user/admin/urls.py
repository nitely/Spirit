# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url

from . import views


app_name = 'user'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^admins/$', views.index_admins, name='index-admins'),
    url(r'^mods/$', views.index_mods, name='index-mods'),
    url(r'^unactive/$', views.index_unactive, name='index-unactive'),
    url(r'^edit/(?P<user_id>[0-9]+)/$', views.edit, name='edit'),
]
