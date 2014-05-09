#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.admin.config",
    url(r'^basic/$', 'config_basic', name='admin-config-basic'),
)