# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url

from . import views
import spirit.apps.category.admin.urls
import spirit.apps.comment.flag.admin.urls
import spirit.apps.topic.admin.urls
import spirit.apps.user.admin.urls


urlpatterns = [
    url(r'^$', views.dashboard, name='admin'),
    url(r'^dashboard/$', views.dashboard, name='admin-dashboard'),
    url(r'^config/$', views.config_basic, name='admin-config-basic'),

    url(r'^category/', include(spirit.apps.category.admin.urls)),
    url(r'^comment/flag/', include(spirit.apps.comment.flag.admin.urls)),
    url(r'^topic/', include(spirit.apps.topic.admin.urls)),
    url(r'^user/', include(spirit.apps.user.admin.urls)),
]
