# -*- coding: utf-8 -*-

from django.conf.urls import include, re_path

from . import views
import spirit.category.admin.urls
import spirit.comment.flag.admin.urls
import spirit.topic.admin.urls
import spirit.user.admin.urls


app_name = 'admin'
urlpatterns = [
    re_path(r'^$', views.dashboard, name='index'),
    re_path(r'^dashboard/$', views.dashboard, name='dashboard'),
    re_path(r'^config/$', views.config_basic, name='config-basic'),

    re_path(r'^category/', include(spirit.category.admin.urls)),
    re_path(r'^comment/flag/', include(spirit.comment.flag.admin.urls)),
    re_path(r'^topic/', include(spirit.topic.admin.urls)),
    re_path(r'^user/', include(spirit.user.admin.urls)),
]
