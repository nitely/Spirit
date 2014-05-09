#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns("spirit.views.admin.index",
    url(r'^$', 'dashboard', name='admin-dashboard'),
)