# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import patterns, include, url


urlpatterns = patterns(
    "spirit.apps.admin.views",

    url(r'^$', 'dashboard', name='admin'),
    url(r'^dashboard/$', 'dashboard', name='admin-dashboard'),
    url(r'^config/$', 'config_basic', name='admin-config-basic'),

    url(r'^category/', include('spirit.apps.category.admin.urls')),
    url(r'^comment/flag/', include('spirit.apps.comment.flag.admin.urls')),
    url(r'^topic/', include('spirit.apps.topic.admin.urls')),
    url(r'^user/', include('spirit.apps.user.admin.urls')),
    )
