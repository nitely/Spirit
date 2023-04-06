# -*- coding: utf-8 -*-

from django.urls import re_path

from . import views


app_name = 'user'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^admins/$', views.index_admins, name='index-admins'),
    re_path(r'^mods/$', views.index_mods, name='index-mods'),
    re_path(r'^unactive/$', views.index_unactive, name='index-unactive'),
    re_path(r'^edit/(?P<user_id>[0-9]+)/$', views.edit, name='edit'),
]
